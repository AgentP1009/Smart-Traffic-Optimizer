import cv2
import numpy as np
from ultralytics import YOLO
from datetime import datetime

class LightweightTrafficAnalyzer:
    def __init__(self):
        # Use tiny YOLO model - 5MB download, works on CPU!
        self.model = YOLO('yolov8n.pt')  # 'n' = nano version
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        
    def analyze_traffic(self, camera_source=0):  # 0 = default webcam
        '''Simple one-function traffic analysis'''
        cap = cv2.VideoCapture(camera_source)
        vehicle_counts = []
        
        # Analyze 30 frames for stability
        for _ in range(30):
            ret, frame = cap.read()
            if not ret:
                break
                
            # Run detection (takes ~100ms on CPU)
            results = self.model(frame, verbose=False)
            vehicle_count = self.count_vehicles(results)
            vehicle_counts.append(vehicle_count)
        
        cap.release()
        
        # Use average for stability
        avg_vehicles = int(np.mean(vehicle_counts)) if vehicle_counts else 0
        
        return {
            'vehicle_count': avg_vehicles,
            'congestion_level': 'High' if avg_vehicles > 12 else 'Medium' if avg_vehicles > 5 else 'Low',
            'processing_time': '~100ms per frame',
            'hardware_used': 'CPU only',
            'frames_analyzed': len(vehicle_counts)
        }
    
    def count_vehicles(self, results):
        count = 0
        if results and results[0].boxes is not None:
            for box in results[0].boxes:
                if int(box.cls) in self.vehicle_classes and box.conf > 0.5:
                    count += 1
        return count

# Test function
def test_vision():
    analyzer = LightweightTrafficAnalyzer()
    result = analyzer.analyze_traffic()
    print('🚦 Vision Test Result:', result)
    return result

if __name__ == '__main__':
    test_vision()
