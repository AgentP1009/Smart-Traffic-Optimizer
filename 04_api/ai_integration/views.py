from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ultralytics import YOLO
import tempfile
import os
import threading
import cv2
import time
from datetime import datetime

# Load YOLO model once when the app starts
try:
    yolo_model = YOLO('../05_models/yolov8n.pt')  # Path from 04_api to 05_models
    YOLO_AVAILABLE = True
    print("✅ YOLO model loaded successfully for API")
except Exception as e:
    YOLO_AVAILABLE = False
    print(f"❌ YOLO model failed to load: {e}")

# Global variables for live detection
live_detector = None
detection_thread = None

class LiveTrafficDetector:
    def __init__(self, model):
        self.model = model
        self.cap = None
        self.is_running = False
        self.detection_results = []
        self.vehicle_classes = ['car', 'motorcycle', 'bus', 'truck']
        self.frame_count = 0
        self.start_time = None
        
    def start_webcam(self, camera_id=0):
        """Start webcam detection with better error handling"""
        try:
            print(f"📹 Attempting to open webcam (ID: {camera_id})...")
            self.cap = cv2.VideoCapture(camera_id)
            
            # Test if camera opened successfully
            if not self.cap.isOpened():
                print(f"❌ Webcam {camera_id} failed to open")
                return False, f"Could not open webcam {camera_id}"
            
            # Test if we can read a frame
            ret, frame = self.cap.read()
            if not ret:
                print(f"❌ Webcam {camera_id} opened but cannot read frames")
                self.cap.release()
                return False, f"Webcam {camera_id} cannot read frames"
            
            print(f"✅ Webcam {camera_id} initialized successfully")
            self.is_running = True
            self.start_time = time.time()
            self.frame_count = 0
            self.detection_results = []
            return True, f"Webcam {camera_id} started successfully"
            
        except Exception as e:
            print(f"❌ Webcam error: {str(e)}")
            if self.cap:
                self.cap.release()
            return False, f"Webcam error: {str(e)}"
    
    def start_ip_camera(self, rtsp_url):
        """Start IP camera detection"""
        try:
            self.cap = cv2.VideoCapture(rtsp_url)
            if not self.cap.isOpened():
                return False, "Could not connect to IP camera"
                
            self.is_running = True
            self.start_time = time.time()
            self.frame_count = 0
            self.detection_results = []
            return True, "IP camera connected successfully"
        except Exception as e:
            return False, f"IP camera error: {str(e)}"
    
    def process_frame(self):
        """Process one frame for detection"""
        if not self.is_running or not self.cap:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            self.is_running = False
            return None
        
        self.frame_count += 1
        
        # Run YOLO detection every 5 frames for performance
        if self.frame_count % 5 == 0:
            results = self.model(frame)
            self._process_detections(results)
        
        return self.get_live_stats()
    
    def _process_detections(self, results):
        """Process YOLO detection results"""
        current_detections = []
        
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
        
        # Update results (keep last 50 detections)
        self.detection_results = (self.detection_results + current_detections)[-50:]
    
    def get_live_stats(self):
        """Get current detection statistics"""
        if not self.is_running:
            return None
            
        # Calculate FPS
        current_time = time.time()
        fps = self.frame_count / (current_time - self.start_time) if self.start_time else 0
        
        return {
            'is_running': self.is_running,
            'total_vehicles_detected': len(self.detection_results),
            'vehicles_by_type': self._count_vehicles_by_type(),
            'latest_detections': self.detection_results[-10:] if self.detection_results else [],
            'fps': round(fps, 2),
            'frame_count': self.frame_count,
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
        self.detection_results = []
        print("🛑 Live detection stopped")

def run_live_detection(detector, camera_type, camera_url):
    """Run live detection in a thread - SIMPLIFIED"""
    try:
        if camera_type == 'webcam':
            # Convert camera_url to integer, default to 0
            cam_id = int(camera_url) if camera_url.isdigit() else 0
            success, message = detector.start_webcam(cam_id)
        else:  # ip_camera
            success, message = detector.start_ip_camera(camera_url)
            
        if success:
            print(f"🎥 Live detection started: {message}")
            
            # Simple detection loop that runs for a short time
            # In a full implementation, this would be a continuous loop
            for i in range(50):  # Process 50 frames max
                if not detector.is_running:
                    break
                detector.process_frame()
                time.sleep(0.1)  # Slow down the loop
                
            print("✅ Live detection completed processing")
        else:
            print(f"❌ Live detection failed: {message}")
            
    except Exception as e:
        print(f"❌ Live detection error: {str(e)}")

@csrf_exempt
def start_live_detection(request):
    """Start live camera detection"""
    global live_detector, detection_thread
    
    if request.method == 'POST':
        try:
            camera_type = request.POST.get('camera_type', 'webcam')
            camera_url = request.POST.get('camera_url', '0')
            
            # Stop existing detection if running
            if live_detector and live_detector.is_running:
                live_detector.stop()
            
            # Create new detector
            live_detector = LiveTrafficDetector(yolo_model)
            
            # Start detection in background thread
            detection_thread = threading.Thread(
                target=run_live_detection,
                args=(live_detector, camera_type, camera_url)
            )
            detection_thread.daemon = True
            detection_thread.start()
            
            # Wait a moment for initialization
            time.sleep(1)
            
            return JsonResponse({
                "success": True,
                "message": "🎥 Live detection started successfully",
                "camera_type": camera_type,
                "camera_url": camera_url,
                "status": "running"
            })
            
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": f"Failed to start live detection: {str(e)}"
            }, status=500)
    
    # GET request - show live detection info
    return JsonResponse({
        "message": "🎥 Live Camera Detection API",
        "description": "Start real-time vehicle detection from camera feeds",
        "supported_cameras": ["webcam", "ip_camera"],
        "current_status": live_detector.get_live_stats() if live_detector else "not_running",
        "usage": {
            "webcam": 'POST {"camera_type": "webcam", "camera_url": "0"}',
            "ip_camera": 'POST {"camera_type": "ip_camera", "camera_url": "rtsp://your-camera-url"}'
        }
    })

@csrf_exempt
def stop_live_detection(request):
    """Stop live camera detection"""
    global live_detector
    
    if request.method == 'POST':
        try:
            if live_detector and live_detector.is_running:
                live_detector.stop()
                return JsonResponse({
                    "success": True,
                    "message": "🛑 Live detection stopped successfully",
                    "status": "stopped"
                })
            else:
                return JsonResponse({
                    "success": False,
                    "error": "No live detection running"
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": f"Failed to stop live detection: {str(e)}"
            }, status=500)
    
    return JsonResponse({
        "message": "Stop Live Detection API",
        "description": "Stop the currently running live camera detection",
        "usage": "POST to this endpoint to stop live detection"
    })

@csrf_exempt
def get_live_stats(request):
    """Get current live detection statistics"""
    global live_detector
    
    if live_detector:
        stats = live_detector.get_live_stats()
        if stats:
            return JsonResponse({
                "success": True,
                "live_detection": stats,
                "status": "running"
            })
    
    return JsonResponse({
        "success": True,
        "live_detection": {
            "is_running": False,
            "message": "No live detection active"
        },
        "status": "stopped"
    })

@csrf_exempt
def detect_vehicles(request):
    if request.method == 'POST':
        if request.FILES.get('image'):
            image_file = request.FILES['image']
            
            if not YOLO_AVAILABLE:
                # Fallback to simulation if YOLO not available
                return JsonResponse({
                    "success": True,
                    "message": "⚠️ Using simulation (YOLO not available)",
                    "vehicles_detected": 4,
                    "processing_time": "0.45s",
                    "detections": [
                        {"vehicle": "motorcycle", "confidence": 0.92, "count": 2},
                        {"vehicle": "car", "confidence": 0.87, "count": 1},
                        {"vehicle": "tuktuk", "confidence": 0.78, "count": 1}
                    ],
                    "is_real_ai": False
                })
            
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    for chunk in image_file.chunks():
                        tmp_file.write(chunk)
                    temp_path = tmp_file.name
                
                # Run REAL YOLO detection
                results = yolo_model(temp_path)
                
                # Process results
                detections = []
                vehicle_classes = ['car', 'motorcycle', 'bus', 'truck']
                vehicle_count = 0
                
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        class_name = yolo_model.names[cls]
                        
                        # Filter for vehicles only
                        if class_name in vehicle_classes:
                            detections.append({
                                "vehicle": class_name,
                                "confidence": round(conf, 2),
                                "bbox": box.xyxy[0].tolist()  # Bounding box coordinates
                            })
                            vehicle_count += 1
                
                # Clean up temporary file
                os.unlink(temp_path)
                
                return JsonResponse({
                    "success": True,
                    "message": "✅ Real YOLO detection completed!",
                    "vehicles_detected": vehicle_count,
                    "processing_time": f"{results[0].speed['inference']:.1f}ms",
                    "detections": detections,
                    "model": "YOLOv8n",
                    "is_real_ai": True
                })
                
            except Exception as e:
                return JsonResponse({
                    "success": False,
                    "error": f"YOLO detection failed: {str(e)}"
                }, status=500)
        
        return JsonResponse({
            "success": False,
            "error": "No image provided for detection"
        }, status=400)
    
    # GET request - show detection info
    return JsonResponse({
        "message": "🔍 Real YOLO Vehicle Detection API",
        "description": "Upload an image for REAL YOLOv8 vehicle detection",
        "supported_vehicles": ["car", "motorcycle", "bus", "truck"],
        "model_status": "YOLOv8n - Real AI" if YOLO_AVAILABLE else "YOLOv8n - Not loaded",
        "example_usage": 'curl -X POST -F "image=@traffic.jpg" http://localhost:8000/api/detect/',
        "is_real_ai": YOLO_AVAILABLE
    })

# ✅ ADD THIS FUNCTION - AI Models endpoint using real database data
@csrf_exempt
def ai_models(request):
    """Get all AI models from database"""
    from .models import AIModel
    
    if request.method == 'GET':
        models = AIModel.objects.all()
        models_list = []
        
        for model in models:
            models_list.append({
                "id": model.id,
                "name": model.name,
                "model_type": model.model_type,
                "version": model.version,
                "is_active": model.is_active,
                "accuracy": model.accuracy,
                "classes": model.classes.split(",") if model.classes else []
            })

        return JsonResponse({
            "message": "AI Models from Database",
            "total_models": len(models_list),
            "models": models_list
        })
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)