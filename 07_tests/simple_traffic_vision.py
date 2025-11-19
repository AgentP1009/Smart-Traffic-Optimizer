import cv2
from ultralytics import YOLO
from datetime import datetime

class InstantTrafficAI:
    def __init__(self):
        self.model = YOLO('yolov8n.pt')  # Auto-downloads 5MB model
        self.vehicle_classes = [2, 3, 5, 7]  # COCO dataset classes
        
    def analyze_webcam(self):
        '''Use your laptop webcam immediately'''
        cap = cv2.VideoCapture(0)  # 0 = built-in webcam
        vehicle_counts = []
        
        print('📹 Starting webcam analysis... (Press Q to stop)')
        
        for i in range(50):  # Analyze 50 frames
            ret, frame = cap.read()
            if not ret:
                break
                
            results = self.model(frame, verbose=False)
            vehicle_count = self.count_vehicles(results)
            vehicle_counts.append(vehicle_count)
            
            # Show live preview
            cv2.putText(frame, f'Vehicles: {vehicle_count}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Traffic Analysis', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        avg_vehicles = sum(vehicle_counts) // len(vehicle_counts) if vehicle_counts else 0
        
        return self.get_traffic_decision(avg_vehicles)
    
    def analyze_image(self, image_path):
        '''Or use a static image file'''
        results = self.model(image_path, verbose=False)
        vehicle_count = self.count_vehicles(results)
        return self.get_traffic_decision(vehicle_count)
    
    def count_vehicles(self, results):
        count = 0
        if results and results[0].boxes is not None:
            for box in results[0].boxes:
                if int(box.cls) in self.vehicle_classes and box.conf > 0.5:
                    count += 1
        return count
    
    def get_traffic_decision(self, vehicle_count):
        congestion = 'High' if vehicle_count > 12 else 'Medium' if vehicle_count > 5 else 'Low'
        action = 'Extend green time' if vehicle_count > 10 else 'Reduce green time' if vehicle_count < 3 else 'Maintain current'
        
        return {
            'vehicle_count': vehicle_count,
            'congestion_level': congestion,
            'suggested_action': action,
            'confidence': 'High - Visual confirmation',
            'timestamp': datetime.now().isoformat()
        }

# USAGE
if __name__ == '__main__':
    ai = InstantTrafficAI()
    print('🚀 Starting AI Traffic Vision System...')
    
    # Test with webcam
    result = ai.analyze_webcam()
    print('\n🎯 AI Traffic Analysis Result:')
    for key, value in result.items():
        print(f'   {key}: {value}')
