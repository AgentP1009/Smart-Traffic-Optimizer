import cv2
import numpy as np
from ultralytics import YOLO
import yt_dlp
import time
import os
import json
from datetime import datetime

print("🚗 YOUTUBE VEHICLE TRACKER")
print("==============================")
print(f"📺 Tracking: https://youtu.be/d6Q1yUatNUU")
print("==============================")

# Load YOLO model
model = YOLO('yolov8n.pt')  # You can use 'yolov8s.pt' for better accuracy
print("✅ YOLOv8 model loaded successfully")

# Vehicle classes from COCO dataset
VEHICLE_CLASSES = {
    2: 'car',
    3: 'motorcycle',
    5: 'bus',
    7: 'truck'
}

# Colors for different vehicle types
VEHICLE_COLORS = {
    'car': (0, 255, 0),        # Green
    'motorcycle': (255, 255, 0), # Yellow
    'bus': (255, 0, 0),        # Blue
    'truck': (0, 0, 255)       # Red
}

class VehicleTracker:
    """Main vehicle tracking system"""
    
    def __init__(self, youtube_url):
        self.youtube_url = youtube_url
        self.video_path = None
        self.cap = None
        self.frame_count = 0
        self.total_frames = 0
        self.fps = 0
        self.width = 0
        self.height = 0
        
        # Tracking data
        self.tracked_vehicles = {}  # vehicle_id -> {'type': type, 'history': [], 'frames_seen': 0}
        self.next_vehicle_id = 0
        self.vehicle_counts = []  # vehicles per frame
        
        # Statistics
        self.start_time = 0
        self.total_vehicles = 0
        
    def download_video(self):
        """Download YouTube video"""
        print("\n📥 DOWNLOADING YOUTUBE VIDEO")
        print("==============================")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_path = f"youtube_video_{timestamp}.mp4"
        
        ydl_opts = {
            'format': 'best[height<=720]',  # Download 720p for faster processing
            'outtmpl': self.video_path,
            'quiet': False,
            'noprogress': False,
            'progress_hooks': [self.download_progress]
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"⏬ Downloading from: {self.youtube_url}")
                info = ydl.extract_info(self.youtube_url, download=True)
                
                print(f"\n✅ Download Complete!")
                print(f"   Title: {info['title']}")
                print(f"   Duration: {info['duration']} seconds")
                print(f"   File: {self.video_path}")
                
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def download_progress(self, d):
        """Show download progress"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            print(f"   Progress: {percent} | Speed: {speed} | ETA: {eta}", end='\r')
        elif d['status'] == 'finished':
            print("\n" + " " * 80, end='\r')
    
    def setup_video(self):
        """Setup video capture"""
        print("\n🎬 SETTING UP VIDEO PROCESSING")
        print("==============================")
        
        self.cap = cv2.VideoCapture(self.video_path)
        
        if not self.cap.isOpened():
            print("❌ Failed to open video file")
            return False
        
        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"📊 Video Information:")
        print(f"   Resolution: {self.width}x{self.height}")
        print(f"   FPS: {self.fps:.1f}")
        print(f"   Total Frames: {self.total_frames}")
        print(f"   Duration: {self.total_frames/self.fps:.1f} seconds")
        
        return True
    
    def match_vehicle(self, x, y, w, h):
        """Match new detection with existing tracked vehicles"""
        center_x = x + w // 2
        center_y = y + h // 2
        
        for vehicle_id, vehicle_data in self.tracked_vehicles.items():
            if not vehicle_data['history']:
                continue
                
            # Get last known position
            last_x, last_y = vehicle_data['history'][-1]
            
            # Calculate distance
            distance = np.sqrt((center_x - last_x)**2 + (center_y - last_y)**2)
            
            # If close enough, it's probably the same vehicle
            if distance < 50:  # Threshold in pixels
                return vehicle_id
        
        return None
    
    def update_tracker(self, detections):
        """Update vehicle tracker with new detections"""
        current_frame_vehicles = 0
        matched_ids = []
        
        for detection in detections:
            x, y, w, h, confidence, vehicle_type = detection
            
            # Try to match with existing vehicle
            vehicle_id = self.match_vehicle(x, y, w, h)
            
            if vehicle_id is None:
                # New vehicle
                vehicle_id = self.next_vehicle_id
                self.next_vehicle_id += 1
                
                self.tracked_vehicles[vehicle_id] = {
                    'type': vehicle_type,
                    'history': [],
                    'frames_seen': 0,
                    'first_seen': self.frame_count,
                    'color': VEHICLE_COLORS.get(vehicle_type, (255, 255, 255))
                }
            
            # Update vehicle data
            center_x = x + w // 2
            center_y = y + h // 2
            
            self.tracked_vehicles[vehicle_id]['history'].append((center_x, center_y))
            self.tracked_vehicles[vehicle_id]['frames_seen'] += 1
            
            # Keep only recent history (last 50 positions)
            if len(self.tracked_vehicles[vehicle_id]['history']) > 50:
                self.tracked_vehicles[vehicle_id]['history'].pop(0)
            
            matched_ids.append((vehicle_id, detection))
            current_frame_vehicles += 1
        
        # Remove vehicles not seen in last 30 frames
        to_remove = []
        for vehicle_id, vehicle_data in self.tracked_vehicles.items():
            if vehicle_id not in [vid for vid, _ in matched_ids]:
                if self.frame_count - vehicle_data['first_seen'] - vehicle_data['frames_seen'] > 30:
                    to_remove.append(vehicle_id)
        
        for vehicle_id in to_remove:
            del self.tracked_vehicles[vehicle_id]
        
        self.vehicle_counts.append(current_frame_vehicles)
        
        return matched_ids, current_frame_vehicles
    
    def process_frame(self, frame):
        """Process a single frame for vehicle detection"""
        # Resize for faster processing while maintaining aspect ratio
        display_height = 600
        display_width = int(self.width * (display_height / self.height))
        
        display_frame = cv2.resize(frame, (display_width, display_height))
        process_frame = cv2.resize(frame, (640, 480))
        
        # Run YOLO detection
        results = model(process_frame, conf=0.3, verbose=False)
        
        detections = []
        
        # Parse detections
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    cls = int(box.cls[0])
                    confidence = float(box.conf[0])
                    
                    if cls in VEHICLE_CLASSES:
                        # Get bounding box
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        # Scale coordinates back to display size
                        scale_x = display_width / 640
                        scale_y = display_height / 480
                        
                        x1, x2 = int(x1 * scale_x), int(x2 * scale_x)
                        y1, y2 = int(y1 * scale_y), int(y2 * scale_y)
                        
                        width = x2 - x1
                        height = y2 - y1
                        vehicle_type = VEHICLE_CLASSES[cls]
                        
                        detections.append((x1, y1, width, height, confidence, vehicle_type))
        
        # Update tracker
        tracked_vehicles, vehicle_count = self.update_tracker(detections)
        
        # Draw on display frame
        for vehicle_id, detection in tracked_vehicles:
            x, y, w, h, confidence, vehicle_type = detection
            vehicle_data = self.tracked_vehicles[vehicle_id]
            color = vehicle_data['color']
            
            # Draw bounding box
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw label with ID
            label = f"ID:{vehicle_id} {vehicle_type} {confidence:.2f}"
            cv2.putText(display_frame, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw tracking trail
            history = vehicle_data['history']
            if len(history) > 1:
                for i in range(1, len(history)):
                    # Draw trail with fading opacity
                    opacity = int(255 * (i / len(history)))
                    trail_color = tuple(int(c * opacity / 255) for c in color)
                    thickness = max(1, int(3 * (i / len(history))))
                    
                    cv2.line(display_frame, history[i-1], history[i], 
                            trail_color, thickness)
        
        return display_frame, vehicle_count, tracked_vehicles
    
    def draw_hud(self, frame, vehicle_count, tracked_vehicles):
        """Draw heads-up display information"""
        hud_height = 150
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], hud_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        y_offset = 30
        
        # Title
        cv2.putText(frame, "🚗 YOUTUBE VEHICLE TRACKER", (20, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
        y_offset += 40
        
        # Active vehicles
        cv2.putText(frame, f"Active Vehicles: {vehicle_count}", (20, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        y_offset += 30
        
        # Total unique vehicles
        cv2.putText(frame, f"Total Unique: {self.next_vehicle_id}", (20, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        y_offset += 30
        
        # Vehicle type breakdown
        type_counts = {}
        for _, detection in tracked_vehicles:
            vehicle_type = detection[5]
            type_counts[vehicle_type] = type_counts.get(vehicle_type, 0) + 1
        
        for vehicle_type, count in type_counts.items():
            color = VEHICLE_COLORS.get(vehicle_type, (255, 255, 255))
            cv2.putText(frame, f"{vehicle_type}: {count}", (250, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            y_offset += 25
        
        # Progress bar at bottom
        progress = min(100, (self.frame_count / self.total_frames) * 100)
        bar_width = frame.shape[1] - 40
        bar_height = 20
        bar_x, bar_y = 20, frame.shape[0] - 40
        
        # Background
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                     (50, 50, 50), -1)
        
        # Progress
        fill_width = int(bar_width * progress / 100)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), 
                     (0, 255, 0), -1)
        
        # Progress text
        progress_text = f"Progress: {progress:.1f}% | Frame: {self.frame_count}/{self.total_frames}"
        cv2.putText(frame, progress_text, (bar_x + 10, bar_y + 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # FPS counter
        elapsed = time.time() - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        cv2.putText(frame, f"FPS: {fps:.1f}", (frame.shape[1] - 100, bar_y + 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return frame
    
    def run_tracking(self):
        """Main tracking loop"""
        print("\n🎯 STARTING VEHICLE TRACKING")
        print("==============================")
        print("Controls:")
        print("  [Q] - Quit")
        print("  [P] - Pause/Resume")
        print("  [S] - Save screenshot")
        print("  [Space] - Step forward (when paused)")
        print("==============================")
        
        self.start_time = time.time()
        paused = False
        step_frame = False
        
        while True:
            if not paused or step_frame:
                ret, frame = self.cap.read()
                step_frame = False
                
                if not ret:
                    break
                
                self.frame_count += 1
                
                # Skip frames for faster processing (process every 2nd frame)
                if self.frame_count % 2 != 0:
                    continue
                
                # Process frame
                display_frame, vehicle_count, tracked_vehicles = self.process_frame(frame)
                
                # Add HUD
                display_frame = self.draw_hud(display_frame, vehicle_count, tracked_vehicles)
                
                # Show frame
                cv2.imshow("YouTube Vehicle Tracker", display_frame)
                
                # Print progress every 100 frames
                if self.frame_count % 100 == 0:
                    elapsed = time.time() - self.start_time
                    fps = self.frame_count / elapsed if elapsed > 0 else 0
                    print(f"📊 Frame {self.frame_count}/{self.total_frames} "
                          f"({(self.frame_count/self.total_frames)*100:.1f}%) | "
                          f"Vehicles: {vehicle_count} | FPS: {fps:.1f}")
            
            # Handle keyboard input
            key = cv2.waitKey(1 if not paused else 0) & 0xFF
            
            if key == ord('q'):
                print("\n⏹️ Stopping tracking...")
                break
            elif key == ord('p'):
                paused = not paused
                status = "⏸️ Paused" if paused else "▶️ Resumed"
                print(status)
            elif key == ord('s'):
                # Save screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"tracking_screenshot_{timestamp}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"📸 Screenshot saved: {filename}")
            elif key == 32:  # Spacebar
                if paused:
                    step_frame = True
        
        self.cap.release()
        cv2.destroyAllWindows()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate tracking report"""
        print("\n📊 TRACKING REPORT")
        print("==============================")
        
        total_time = time.time() - self.start_time
        video_duration = self.total_frames / self.fps
        
        print(f"📈 Statistics:")
        print(f"   Total Frames Processed: {self.frame_count}")
        print(f"   Total Unique Vehicles Tracked: {self.next_vehicle_id}")
        print(f"   Max Vehicles in Frame: {max(self.vehicle_counts) if self.vehicle_counts else 0}")
        print(f"   Avg Vehicles per Frame: {np.mean(self.vehicle_counts):.1f}")
        print(f"   Video Duration: {video_duration:.1f} seconds")
        print(f"   Processing Time: {total_time:.1f} seconds")
        print(f"   Processing Speed: {self.frame_count/total_time:.1f} FPS")
        print(f"   Real-time Factor: {video_duration/total_time:.2f}x")
        
        # Vehicle type breakdown
        print(f"\n🚗 Vehicle Types:")
        type_counts = {}
        for vehicle_data in self.tracked_vehicles.values():
            vehicle_type = vehicle_data['type']
            type_counts[vehicle_type] = type_counts.get(vehicle_type, 0) + 1
        
        for vehicle_type, count in type_counts.items():
            print(f"   {vehicle_type}: {count}")
        
        # Save report to file
        report_data = {
            'youtube_url': self.youtube_url,
            'total_frames': int(self.frame_count),
            'unique_vehicles': int(self.next_vehicle_id),
            'max_vehicles_per_frame': int(max(self.vehicle_counts) if self.vehicle_counts else 0),
            'avg_vehicles_per_frame': float(np.mean(self.vehicle_counts)),
            'processing_time': float(total_time),
            'processing_fps': float(self.frame_count/total_time),
            'vehicle_breakdown': type_counts,
            'timestamp': datetime.now().isoformat()
        }
        
        report_file = f"tracking_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Report saved to: {report_file}")
        print("\n🎉 Tracking completed successfully!")
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
        # Ask about deleting downloaded video
        if self.video_path and os.path.exists(self.video_path):
            response = input(f"\n🗑️ Delete downloaded video ({os.path.basename(self.video_path)})? (y/n): ")
            if response.lower() == 'y':
                os.remove(self.video_path)
                print("✅ Video deleted")

def main():
    """Main function"""
    # YouTube URL to track
    youtube_url = "https://youtu.be/d6Q1yUatNUU"
    
    print("\n🚗 YOUTUBE VEHICLE TRACKING SYSTEM")
    print("=====================================")
    print("This system will:")
    print("1. Download the YouTube video")
    print("2. Track vehicles using YOLOv8")
    print("3. Show real-time tracking with trails")
    print("4. Generate a detailed report")
    print("=====================================")
    
    # Create tracker
    tracker = VehicleTracker(youtube_url)
    
    try:
        # Step 1: Download video
        if not tracker.download_video():
            return
        
        # Step 2: Setup video processing
        if not tracker.setup_video():
            return
        
        # Step 3: Run tracking
        tracker.run_tracking()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tracking interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during tracking: {e}")
    finally:
        tracker.cleanup()

if __name__ == "__main__":
    # Install required packages if not installed
    try:
        import cv2
        import yt_dlp
        from ultralytics import YOLO
    except ImportError:
        print("\n📦 Installing required packages...")
        import subprocess
        subprocess.check_call(["pip", "install", "opencv-python", "numpy", "ultralytics", "yt-dlp"])
        print("✅ Packages installed successfully!")
    
    main()