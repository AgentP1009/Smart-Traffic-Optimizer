import cv2
import time
from ultralytics import YOLO
import numpy as np
import threading
from datetime import datetime

class LiveTrafficDetector:
    def __init__(self, model_path='../05_models/yolov8n.pt'):
        """Initialize live traffic detector with YOLO model"""
        print("🚀 Initializing Live Traffic Detector...")
        self.model = YOLO(model_path)
        self.cap = None
        self.is_running = False
        self.detection_results = []
        self.vehicle_classes = ['car', 'motorcycle', 'bus', 'truck']
        
    def start_webcam(self, camera_id=0):
        """Start webcam detection"""
        print(f"📹 Starting webcam (ID: {camera_id})...")
        self.cap = cv2.VideoCapture(camera_id)
        
        if not self.cap.isOpened():
            print("❌ Error: Could not open webcam")
            return False
            
        self.is_running = True
        print("✅ Webcam started successfully!")
        self._run_detection_loop()
        return True
    
    def start_ip_camera(self, rtsp_url):
        """Start IP camera detection"""
        print(f"🌐 Connecting to IP camera: {rtsp_url}")
        self.cap = cv2.VideoCapture(rtsp_url)
        
        if not self.cap.isOpened():
            print("❌ Error: Could not connect to IP camera")
            return False
            
        self.is_running = True
        print("✅ IP camera connected successfully!")
        self._run_detection_loop()
        return True
    
    def _run_detection_loop(self):
        """Main detection loop"""
        frame_count = 0
        start_time = time.time()
        
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                print("❌ Error: Could not read frame")
                break
            
            # Run YOLO detection every 5 frames for performance
            if frame_count % 5 == 0:
                results = self.model(frame)
                self._process_detections(results, frame)
            
            # Display frame with detections
            self._display_frame(frame)
            
            frame_count += 1
            
            # Break on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Calculate FPS
        end_time = time.time()
        fps = frame_count / (end_time - start_time)
        print(f"📊 Average FPS: {fps:.2f}")
        
        self.stop()
    
    def _process_detections(self, results, frame):
        """Process YOLO detection results"""
        current_detections = []
        vehicle_count = 0
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.model.names[cls]
                
                # Filter for vehicles only
                if class_name in self.vehicle_classes:
                    bbox = box.xyxy[0].tolist()
                    current_detections.append({
                        'vehicle': class_name,
                        'confidence': round(conf, 2),
                        'bbox': bbox,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
                    vehicle_count += 1
                    
                    # Draw bounding box on frame
                    x1, y1, x2, y2 = map(int, bbox)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f'{class_name} {conf:.2f}', 
                               (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Update results
        self.detection_results = current_detections
        
        # Print real-time stats
        print(f"🚗 Vehicles detected: {vehicle_count} | Latest: {[d['vehicle'] for d in current_detections]}")
    
    def _display_frame(self, frame):
        """Display frame with detection information"""
        # Add stats overlay
        stats_text = f"Vehicles: {len(self.detection_results)} | Time: {datetime.now().strftime('%H:%M:%S')}"
        cv2.putText(frame, stats_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Display frame
        cv2.imshow('Smart Traffic Optimizer - Live Detection', frame)
    
    def get_live_stats(self):
        """Get current detection statistics"""
        return {
            'total_vehicles': len(self.detection_results),
            'vehicles_by_type': self._count_vehicles_by_type(),
            'latest_detections': self.detection_results[-5:] if self.detection_results else [],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _count_vehicles_by_type(self):
        """Count vehicles by type"""
        count = {}
        for detection in self.detection_results:
            vehicle_type = detection['vehicle']
            count[vehicle_type] = count.get(vehicle_type, 0) + 1
        return count
    
    def stop(self):
        """Stop detection and cleanup"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("🛑 Live detection stopped")

# Usage examples
def demo_webcam():
    """Demo with webcam"""
    detector = LiveTrafficDetector()
    detector.start_webcam(0)  # 0 = default webcam

def demo_ip_camera():
    """Demo with IP camera (example URLs)"""
    detector = LiveTrafficDetector()
    
    # Common IP camera RTSP URLs (replace with your camera)
    rtsp_urls = [
        "rtsp://admin:password@192.168.1.100:554/stream1",
        "rtsp://192.168.1.101:8554/live.sdp",
        # Add your camera URLs here
    ]
    
    for url in rtsp_urls:
        if detector.start_ip_camera(url):
            break
    else:
        print("❌ No IP cameras available, falling back to webcam...")
        detector.start_webcam(0)

if __name__ == "__main__":
    print("🎥 Smart Traffic Optimizer - Live Camera Demo")
    print("Options:")
    print("1. Webcam detection")
    print("2. IP camera detection")
    
    choice = input("Select option (1 or 2): ").strip()
    
    if choice == "2":
        demo_ip_camera()
    else:
        demo_webcam()