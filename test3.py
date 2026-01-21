import cv2
import numpy as np
from ultralytics import YOLO
import yt_dlp
import time
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter

print("🚗 YOUTUBE TRAFFIC ANALYZER")
print("================================")
print(f"📺 Analyzing: https://youtu.be/Fzr7i4Ko56Q")
print("================================")

# Load YOLO model
model = YOLO('yolov8n.pt')  # Using nano model for speed
print("✅ YOLOv8 model loaded successfully")

# Vehicle classes with expanded detection
VEHICLE_CLASSES = {
    0: 'person',        # For context
    1: 'bicycle',
    2: 'car',
    3: 'motorcycle',
    5: 'bus',
    6: 'train',
    7: 'truck',
    8: 'boat',
    9: 'traffic light',  # For traffic analysis
}

# Colors for visualization
VEHICLE_COLORS = {
    'car': (0, 255, 0),        # Green
    'bus': (0, 165, 255),      # Orange
    'truck': (0, 0, 255),      # Red
    'motorcycle': (255, 255, 0), # Cyan
    'bicycle': (255, 0, 255),   # Magenta
    'person': (255, 255, 255),  # White
    'train': (139, 0, 139),     # Purple
    'traffic light': (0, 255, 255), # Yellow
    'default': (200, 200, 200)  # Gray
}

class TrafficAnalyzer:
    """Comprehensive traffic analysis system"""
    
    def __init__(self, youtube_url):
        self.youtube_url = youtube_url
        self.video_path = None
        self.cap = None
        
        # Video properties
        self.frame_count = 0
        self.total_frames = 0
        self.fps = 30  # Default
        self.width = 0
        self.height = 0
        
        # Tracking system
        self.tracked_objects = {}
        self.next_id = 0
        self.frame_history = []
        
        # Traffic statistics
        self.vehicle_counts_per_frame = []
        self.speed_estimates = {}
        self.lane_data = {}
        
        # Performance tracking
        self.start_time = 0
        self.processing_times = []
        
        # Detection zones (for traffic analysis)
        self.detection_zones = []
        
    def download_video(self):
        """Download YouTube video with high quality"""
        print("\n📥 DOWNLOADING VIDEO")
        print("====================")
        
        # Create output directory
        if not os.path.exists('videos'):
            os.makedirs('videos')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_path = f"videos/traffic_analysis_{timestamp}.mp4"
        
        # YouTube DL options
        ydl_opts = {
            'format': 'best[height<=1080]',  # 1080p for better quality
            'outtmpl': self.video_path,
            'quiet': False,
            'noprogress': False,
            'progress_hooks': [self.show_progress],
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
        
        try:
            print(f"🔗 Source: {self.youtube_url}")
            print(f"💾 Saving to: {self.video_path}")
            print("⏳ Downloading...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.youtube_url, download=True)
                
                print(f"\n✅ Download Complete!")
                print(f"   Title: {info.get('title', 'Unknown')}")
                print(f"   Duration: {info.get('duration', 0)} seconds")
                print(f"   Views: {info.get('view_count', 'N/A')}")
                print(f"   Upload Date: {info.get('upload_date', 'N/A')}")
                
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {str(e)}")
            return False
    
    def show_progress(self, d):
        """Display download progress"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').replace('%', '')
            try:
                percent_float = float(percent)
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                
                # Create progress bar
                bar_length = 40
                filled = int(bar_length * percent_float / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                
                print(f"   [{bar}] {percent_float:.1f}% | Speed: {speed} | ETA: {eta}", end='\r')
            except:
                pass
        elif d['status'] == 'finished':
            print("\n" + " " * 100, end='\r')
    
    def setup_video_analysis(self):
        """Initialize video for analysis"""
        print("\n🎬 VIDEO ANALYSIS SETUP")
        print("=======================")
        
        if not os.path.exists(self.video_path):
            print("❌ Video file not found")
            return False
        
        self.cap = cv2.VideoCapture(self.video_path)
        
        if not self.cap.isOpened():
            print("❌ Failed to open video file")
            return False
        
        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Set up detection zones based on video aspect ratio
        self.setup_detection_zones()
        
        print(f"📊 Video Properties:")
        print(f"   Resolution: {self.width}x{self.height}")
        print(f"   Frame Rate: {self.fps:.1f} FPS")
        print(f"   Total Frames: {self.total_frames}")
        print(f"   Duration: {self.total_frames/self.fps:.1f} seconds")
        print(f"   Detection Zones: {len(self.detection_zones)}")
        
        return True
    
    def setup_detection_zones(self):
        """Setup zones for traffic analysis"""
        # Create multiple zones for different parts of the road
        zone_height = self.height // 3
        
        # Zone 1: Entry zone (top)
        self.detection_zones.append({
            'name': 'Entry Zone',
            'roi': (0, 0, self.width, zone_height),
            'color': (0, 255, 0),
            'count': 0
        })
        
        # Zone 2: Middle zone
        self.detection_zones.append({
            'name': 'Middle Zone',
            'roi': (0, zone_height, self.width, zone_height * 2),
            'color': (255, 255, 0),
            'count': 0
        })
        
        # Zone 3: Exit zone (bottom)
        self.detection_zones.append({
            'name': 'Exit Zone',
            'roi': (0, zone_height * 2, self.width, self.height),
            'color': (255, 0, 0),
            'count': 0
        })
    
    def detect_objects(self, frame):
        """Detect vehicles and objects in frame"""
        # Resize for processing while maintaining aspect ratio
        processing_width = 640
        processing_height = int(frame.shape[0] * (processing_width / frame.shape[1]))
        process_frame = cv2.resize(frame, (processing_width, processing_height))
        
        # Run YOLO detection
        results = model(process_frame, conf=0.25, iou=0.5, verbose=False)
        
        detections = []
        
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    
                    if cls_id in VEHICLE_CLASSES:
                        # Get bounding box
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        # Scale to original frame size
                        scale_x = frame.shape[1] / processing_width
                        scale_y = frame.shape[0] / processing_height
                        
                        x1, x2 = int(x1 * scale_x), int(x2 * scale_x)
                        y1, y2 = int(y1 * scale_y), int(y2 * scale_y)
                        
                        width = x2 - x1
                        height = y2 - y1
                        
                        # Calculate center
                        center_x = x1 + width // 2
                        center_y = y1 + height // 2
                        
                        object_type = VEHICLE_CLASSES[cls_id]
                        color = VEHICLE_COLORS.get(object_type, VEHICLE_COLORS['default'])
                        
                        detections.append({
                            'bbox': (x1, y1, width, height),
                            'center': (center_x, center_y),
                            'type': object_type,
                            'confidence': confidence,
                            'color': color,
                            'zone': self.get_zone(center_y)
                        })
        
        return detections
    
    def get_zone(self, y):
        """Determine which zone the object is in"""
        zone_height = self.height // 3
        
        if y < zone_height:
            return 0  # Entry zone
        elif y < zone_height * 2:
            return 1  # Middle zone
        else:
            return 2  # Exit zone
    
    def track_objects(self, detections, frame_num):
        """Track objects across frames"""
        current_ids = []
        
        if not hasattr(self, 'max_distance'):
            self.max_distance = 50  # pixels
        
        for detection in detections:
            center_x, center_y = detection['center']
            
            # Find matching existing track
            matched_id = None
            min_distance = float('inf')
            
            for obj_id, obj_data in self.tracked_objects.items():
                if obj_data['last_seen'] < frame_num - 30:  # Skip stale tracks
                    continue
                
                # Calculate distance to last known position
                last_x, last_y = obj_data['positions'][-1]
                distance = np.sqrt((center_x - last_x)**2 + (center_y - last_y)**2)
                
                # Same type and close enough
                if (obj_data['type'] == detection['type'] and 
                    distance < self.max_distance and 
                    distance < min_distance):
                    min_distance = distance
                    matched_id = obj_id
            
            if matched_id is not None:
                # Update existing track
                obj_id = matched_id
                self.tracked_objects[obj_id]['positions'].append((center_x, center_y))
                self.tracked_objects[obj_id]['last_seen'] = frame_num
                self.tracked_objects[obj_id]['frames'] += 1
                
                # Update speed estimate
                if len(self.tracked_objects[obj_id]['positions']) > 1:
                    self.update_speed_estimate(obj_id)
            else:
                # Create new track
                obj_id = self.next_id
                self.next_id += 1
                
                self.tracked_objects[obj_id] = {
                    'type': detection['type'],
                    'positions': [(center_x, center_y)],
                    'first_seen': frame_num,
                    'last_seen': frame_num,
                    'frames': 1,
                    'speed': 0,
                    'zone_history': [detection['zone']],
                    'color': detection['color']
                }
            
            current_ids.append((obj_id, detection))
        
        # Clean up old tracks
        self.cleanup_tracks(frame_num)
        
        return current_ids
    
    def update_speed_estimate(self, obj_id):
        """Estimate speed based on position changes"""
        positions = self.tracked_objects[obj_id]['positions']
        
        if len(positions) >= 2:
            # Calculate distance moved
            x1, y1 = positions[-2]
            x2, y2 = positions[-1]
            distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            # Convert to pixels per second (assuming 30 FPS)
            speed = distance * self.fps
            
            self.tracked_objects[obj_id]['speed'] = speed
    
    def cleanup_tracks(self, current_frame):
        """Remove tracks that haven't been seen recently"""
        to_remove = []
        
        for obj_id, obj_data in self.tracked_objects.items():
            if current_frame - obj_data['last_seen'] > 60:  # 2 seconds at 30 FPS
                to_remove.append(obj_id)
        
        for obj_id in to_remove:
            del self.tracked_objects[obj_id]
    
    def draw_analysis(self, frame, tracked_objects, frame_num):
        """Draw analysis overlay on frame"""
        display_frame = frame.copy()
        
        # Draw detection zones
        for zone in self.detection_zones:
            x1, y1, x2, y2 = zone['roi']
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), zone['color'], 2)
            cv2.putText(display_frame, zone['name'], (x1 + 10, y1 + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, zone['color'], 2)
        
        # Draw tracked objects
        for obj_id, detection in tracked_objects:
            x, y, w, h = detection['bbox']
            obj_type = detection['type']
            color = detection['color']
            
            # Draw bounding box
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw ID and type
            label = f"ID:{obj_id} {obj_type}"
            cv2.putText(display_frame, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw tracking trail
            if obj_id in self.tracked_objects:
                positions = self.tracked_objects[obj_id]['positions']
                if len(positions) > 1:
                    for i in range(1, len(positions)):
                        alpha = i / len(positions)
                        trail_color = tuple(int(c * alpha) for c in color)
                        cv2.line(display_frame, positions[i-1], positions[i],
                                trail_color, 2)
        
        # Draw statistics overlay
        self.draw_statistics_overlay(display_frame, frame_num)
        
        return display_frame
    
    def draw_statistics_overlay(self, frame, frame_num):
        """Draw statistics overlay"""
        overlay_height = 200
        overlay = np.zeros((overlay_height, frame.shape[1], 3), dtype=np.uint8)
        
        # Current counts
        current_counts = {}
        for obj_id, obj_data in self.tracked_objects.items():
            if obj_data['last_seen'] == frame_num:
                obj_type = obj_data['type']
                current_counts[obj_type] = current_counts.get(obj_type, 0) + 1
        
        # Draw overlay
        y_offset = 30
        
        # Title
        cv2.putText(overlay, "🚦 TRAFFIC ANALYSIS DASHBOARD", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
        y_offset += 40
        
        # Current frame info
        cv2.putText(overlay, f"Frame: {frame_num}/{self.total_frames}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 25
        
        # Active objects
        active_count = len([oid for oid, od in self.tracked_objects.items() 
                          if od['last_seen'] == frame_num])
        cv2.putText(overlay, f"Active Objects: {active_count}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        y_offset += 25
        
        # Total unique objects
        cv2.putText(overlay, f"Total Unique: {self.next_id}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        y_offset += 25
        
        # Object breakdown
        x_offset = 250
        y_offset = 70
        
        for obj_type, count in current_counts.items():
            color = VEHICLE_COLORS.get(obj_type, VEHICLE_COLORS['default'])
            cv2.putText(overlay, f"{obj_type}: {count}", (x_offset, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            y_offset += 20
            if y_offset > 150:
                x_offset += 150
                y_offset = 70
        
        # Zone counts
        x_offset = 450
        y_offset = 70
        
        for i, zone in enumerate(self.detection_zones):
            zone_count = len([oid for oid, od in self.tracked_objects.items() 
                            if od['last_seen'] == frame_num and 
                            od['zone_history'][-1] == i])
            cv2.putText(overlay, f"{zone['name']}: {zone_count}", (x_offset, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, zone['color'], 1)
            y_offset += 20
        
        # Progress bar
        progress = min(100, (frame_num / self.total_frames) * 100)
        bar_width = 600
        bar_x, bar_y = 20, 160
        
        # Background
        cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + bar_width, bar_y + 15),
                     (50, 50, 50), -1)
        
        # Progress
        fill_width = int(bar_width * progress / 100)
        cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + fill_width, bar_y + 15),
                     (0, 255, 0), -1)
        
        # Progress text
        cv2.putText(overlay, f"Progress: {progress:.1f}%", (bar_x + bar_width + 10, bar_y + 12),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Blend overlay with frame
        frame[:overlay_height] = cv2.addWeighted(frame[:overlay_height], 0.3, 
                                                overlay, 0.7, 0)
        
        return frame
    
    def analyze_traffic(self):
        """Main traffic analysis loop"""
        print("\n🔍 ANALYZING TRAFFIC")
        print("====================")
        print("Controls:")
        print("  [Q] - Quit analysis")
        print("  [P] - Pause/Resume")
        print("  [S] - Save screenshot")
        print("  [R] - Reset tracking")
        print("  [Space] - Step frame (when paused)")
        print("====================")
        
        self.start_time = time.time()
        paused = False
        step_frame = False
        
        frame_skip = 2  # Process every 2nd frame for speed
        
        while True:
            if not paused or step_frame:
                ret, frame = self.cap.read()
                step_frame = False
                
                if not ret:
                    break
                
                self.frame_count += 1
                
                # Skip frames for faster processing
                if self.frame_count % frame_skip != 0:
                    continue
                
                # Detect objects
                detections = self.detect_objects(frame)
                
                # Track objects
                tracked = self.track_objects(detections, self.frame_count)
                
                # Update statistics
                self.vehicle_counts_per_frame.append(len(tracked))
                
                # Draw analysis
                display_frame = self.draw_analysis(frame, tracked, self.frame_count)
                
                # Show frame
                cv2.imshow(f"Traffic Analysis - {self.youtube_url}", display_frame)
                
                # Show progress every 100 frames
                if self.frame_count % 100 == 0:
                    elapsed = time.time() - self.start_time
                    fps = self.frame_count / elapsed if elapsed > 0 else 0
                    progress = (self.frame_count / self.total_frames) * 100
                    
                    print(f"📊 Frame: {self.frame_count:6d}/{self.total_frames} "
                          f"({progress:5.1f}%) | "
                          f"Active: {len(tracked):3d} | "
                          f"FPS: {fps:5.1f}")
            
            # Handle keyboard input
            key = cv2.waitKey(1 if not paused else 0) & 0xFF
            
            if key == ord('q'):
                print("\n⏹️ Stopping analysis...")
                break
            elif key == ord('p'):
                paused = not paused
                status = "⏸️ Paused" if paused else "▶️ Resumed"
                print(status)
            elif key == ord('s'):
                self.save_screenshot(display_frame)
            elif key == ord('r'):
                self.reset_tracking()
                print("🔄 Tracking reset")
            elif key == 32:  # Spacebar
                if paused:
                    step_frame = True
        
        self.cap.release()
        cv2.destroyAllWindows()
        
        # Generate comprehensive report
        self.generate_traffic_report()
    
    def save_screenshot(self, frame):
        """Save current frame as screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
        
        filename = f"screenshots/traffic_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"📸 Screenshot saved: {filename}")
    
    def reset_tracking(self):
        """Reset tracking data"""
        self.tracked_objects.clear()
        self.next_id = 0
        print("🔄 Tracking data cleared")
    
    def generate_traffic_report(self):
        """Generate comprehensive traffic analysis report"""
        print("\n📊 TRAFFIC ANALYSIS REPORT")
        print("============================")
        
        total_time = time.time() - self.start_time
        video_duration = self.total_frames / self.fps
        
        print(f"\n📈 SUMMARY STATISTICS")
        print(f"   Total Frames Processed: {self.frame_count:,}")
        print(f"   Unique Objects Tracked: {self.next_id:,}")
        print(f"   Peak Traffic Density: {max(self.vehicle_counts_per_frame) if self.vehicle_counts_per_frame else 0}")
        print(f"   Average Objects per Frame: {np.mean(self.vehicle_counts_per_frame):.1f}")
        print(f"   Video Duration: {video_duration:.1f} seconds")
        print(f"   Analysis Time: {total_time:.1f} seconds")
        print(f"   Processing Speed: {self.frame_count/total_time:.1f} FPS")
        print(f"   Real-time Factor: {video_duration/total_time:.2f}x")
        
        # Object type analysis
        print(f"\n🚗 OBJECT TYPE DISTRIBUTION")
        object_types = []
        for obj_data in self.tracked_objects.values():
            object_types.append(obj_data['type'])
        
        type_counts = Counter(object_types)
        for obj_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(object_types)) * 100 if object_types else 0
            print(f"   {obj_type:15s}: {count:4d} ({percentage:5.1f}%)")
        
        # Zone analysis
        print(f"\n📍 ZONE ANALYSIS")
        zone_counts = [0, 0, 0]
        for obj_data in self.tracked_objects.values():
            if obj_data['zone_history']:
                zone_counts[obj_data['zone_history'][-1]] += 1
        
        for i, zone in enumerate(self.detection_zones):
            percentage = (zone_counts[i] / sum(zone_counts)) * 100 if sum(zone_counts) > 0 else 0
            print(f"   {zone['name']:15s}: {zone_counts[i]:4d} ({percentage:5.1f}%)")
        
        # Save detailed report
        report_data = {
            'youtube_url': self.youtube_url,
            'analysis_date': datetime.now().isoformat(),
            'video_duration': video_duration,
            'analysis_duration': total_time,
            'frames_processed': self.frame_count,
            'unique_objects': self.next_id,
            'peak_density': int(max(self.vehicle_counts_per_frame)) if self.vehicle_counts_per_frame else 0,
            'avg_density': float(np.mean(self.vehicle_counts_per_frame)),
            'object_distribution': dict(type_counts),
            'zone_distribution': {zone['name']: zone_counts[i] for i, zone in enumerate(self.detection_zones)},
            'processing_speed': float(self.frame_count/total_time),
            'realtime_factor': float(video_duration/total_time)
        }
        
        # Save report
        if not os.path.exists('reports'):
            os.makedirs('reports')
        
        report_file = f"reports/traffic_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Generate visualization
        self.generate_visualizations()
        
        print(f"\n🎉 Analysis completed successfully!")
        print(f"   Video: {self.video_path}")
        print(f"   Report: {report_file}")
        print(f"   Screenshots: screenshots/")
    
    def generate_visualizations(self):
        """Generate traffic visualization graphs"""
        if not os.path.exists('visualizations'):
            os.makedirs('visualizations')
        
        # Traffic density over time
        plt.figure(figsize=(12, 6))
        
        # Plot 1: Traffic density
        plt.subplot(1, 2, 1)
        frames = list(range(len(self.vehicle_counts_per_frame)))
        plt.plot(frames, self.vehicle_counts_per_frame, 'b-', alpha=0.7, linewidth=1)
        plt.fill_between(frames, 0, self.vehicle_counts_per_frame, alpha=0.3)
        plt.xlabel('Frame Number')
        plt.ylabel('Number of Objects')
        plt.title('Traffic Density Over Time')
        plt.grid(True, alpha=0.3)
        
        # Plot 2: Object type distribution
        plt.subplot(1, 2, 2)
        object_types = []
        for obj_data in self.tracked_objects.values():
            object_types.append(obj_data['type'])
        
        type_counts = Counter(object_types)
        labels = list(type_counts.keys())
        values = list(type_counts.values())
        
        colors = [VEHICLE_COLORS.get(label, VEHICLE_COLORS['default']) for label in labels]
        # Convert BGR to RGB for matplotlib
        colors = [(c[2]/255, c[1]/255, c[0]/255) for c in colors]
        
        plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Object Type Distribution')
        
        plt.suptitle('Traffic Analysis Visualizations')
        plt.tight_layout()
        
        viz_file = f"visualizations/traffic_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(viz_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"📈 Visualization saved: {viz_file}")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

def main():
    """Main execution function"""
    print("\n🚦 ADVANCED TRAFFIC ANALYSIS SYSTEM")
    print("=====================================")
    print("This system performs:")
    print("1. YouTube video download")
    print("2. Multi-object detection and tracking")
    print("3. Traffic density analysis")
    print("4. Zone-based traffic flow analysis")
    print("5. Comprehensive reporting")
    print("=====================================")
    
    # YouTube URL for analysis
    youtube_url = "https://youtu.be/Fzr7i4Ko56Q"
    
    # Create analyzer
    analyzer = TrafficAnalyzer(youtube_url)
    
    try:
        # Step 1: Download video
        print("\n" + "="*50)
        print("STEP 1: Downloading YouTube video")
        print("="*50)
        if not analyzer.download_video():
            return
        
        # Step 2: Setup analysis
        print("\n" + "="*50)
        print("STEP 2: Setting up analysis")
        print("="*50)
        if not analyzer.setup_video_analysis():
            return
        
        # Step 3: Run analysis
        print("\n" + "="*50)
        print("STEP 3: Running traffic analysis")
        print("="*50)
        analyzer.analyze_traffic()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        analyzer.cleanup()

if __name__ == "__main__":
    # Check and install required packages
    required_packages = [
        'opencv-python',
        'numpy',
        'ultralytics',
        'yt-dlp',
        'matplotlib'
    ]
    
    print("🔍 Checking for required packages...")
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
            elif package == 'numpy':
                import numpy as np
            elif package == 'ultralytics':
                from ultralytics import YOLO
            elif package == 'yt_dlp':
                import yt_dlp
            elif package == 'matplotlib':
                import matplotlib.pyplot as plt
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ⚠️ {package} not found. Installing...")
            import subprocess
            subprocess.check_call(['pip', 'install', package])
            print(f"   ✅ {package} installed")
    
    print("\n✅ All packages ready!")
    
    # Run main function
    main()