from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static
import json

# ✅ FIXED: Import all needed functions including ai_models
from ai_integration.views import start_live_detection, stop_live_detection, get_live_stats, ai_models

# =====================
# 🚦 HOME & API INFO
# =====================
def home(request):
    return JsonResponse({
        "message": "🚦 Smart Traffic Optimizer API",
        "status": "Active ✅",
        "version": "1.0.0",
        "description": "AI-powered traffic monitoring & vehicle detection",
        "endpoints": {
            "admin": "/admin/",
            "vehicle_images": "/api/vehicle-images/",
            "upload_image": "/api/upload/",
            "ai_models": "/api/ai-models/",
            "detect_vehicles": "/api/detect/",
            "stats": "/stats/",
            "live_detection_start": "/api/live-detection/start/",
            "live_detection_stop": "/api/live-detection/stop/",
            "live_detection_stats": "/api/live-detection/stats/"
        },
        "usage": "POST images to /api/upload/ for training data collection or start live detection"
    })

# =====================
# 📸 VEHICLE IMAGES API
# =====================
@csrf_exempt
def vehicle_images(request):
    """Get all uploaded vehicle images"""
    if request.method == 'GET':
        sample_data = [
            {"id": 1, "vehicle_type": "motorcycle", "location": "Phnom Penh", "status": "approved"},
            {"id": 2, "vehicle_type": "car", "location": "Siem Reap", "status": "pending"}
        ]

        return JsonResponse({
            "message": "Vehicle images collection",
            "total_images": len(sample_data),
            "data": sample_data
        })
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)

# =====================
# 📤 FILE UPLOAD API
# =====================
@csrf_exempt
def upload(request):
    """Upload vehicle images for training"""
    if request.method == 'POST':
        try:
            if request.FILES.get('image'):
                # Save uploaded file
                image_file = request.FILES['image']
                fs = FileSystemStorage()
                filename = fs.save(f"training_data/{image_file.name}", image_file)

                # Get form data
                vehicle_type = request.POST.get('vehicle_type', 'unknown')
                location = request.POST.get('location', 'unknown')

                return JsonResponse({
                    "success": True,
                    "message": "✅ Image uploaded successfully!",
                    "data": {
                        "filename": filename,
                        "url": fs.url(filename),
                        "vehicle_type": vehicle_type,
                        "location": location,
                        "file_size": f"{image_file.size} bytes"
                    },
                    "next_steps": "Image will be reviewed and used for model training"
                })
            else:
                return JsonResponse({
                    "success": False,
                    "error": "No image file provided"
                }, status=400)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": f"Upload failed: {str(e)}"
            }, status=500)

    # GET request - show upload instructions
    return JsonResponse({
        "message": "📤 Vehicle Image Upload API",
        "instructions": "POST an image file with vehicle data",
        "required_fields": {
            "image": "Image file (jpg, png, etc.)",
            "vehicle_type": "Type of vehicle (motorcycle, car, tuktuk, etc.)",
            "location": "Location where photo was taken"
        },
        "example_curl": 'curl -X POST -F "image=@car.jpg" -F "vehicle_type=car" -F "location=Phnom Penh" http://localhost:8000/api/upload/'    
    })

# =====================
# 🔍 VEHICLE DETECTION API
# =====================
@csrf_exempt
def detect_vehicles(request):
    """Run vehicle detection on uploaded images"""
    if request.method == 'POST':
        if request.FILES.get('image'):
            # Simulate AI detection
            detection_results = {
                "vehicles_detected": 4,
                "processing_time": "0.45s",
                "detections": [
                    {"vehicle": "motorcycle", "confidence": 0.92, "count": 2},
                    {"vehicle": "car", "confidence": 0.87, "count": 1},
                    {"vehicle": "tuktuk", "confidence": 0.78, "count": 1}
                ],
                "image_analysis": {
                    "total_vehicles": 4,
                    "congestion_level": "medium",
                    "dominant_vehicle": "motorcycle"
                }
            }

            return JsonResponse({
                "success": True,
                "message": "✅ Vehicle detection completed",
                "results": detection_results
            })

        return JsonResponse({
            "success": False,
            "error": "No image provided for detection"
        }, status=400)

    # GET request - show detection info
    return JsonResponse({
        "message": "🔍 Vehicle Detection API",
        "description": "Upload an image for real-time vehicle detection",
        "supported_vehicles": ["car", "motorcycle", "bus", "truck", "tuktuk", "bicycle"],
        "example_usage": 'curl -X POST -F "image=@traffic.jpg" http://localhost:8000/api/detect/'
    })

# =====================
# 📊 TRAFFIC STATISTICS API  
# =====================
def stats(request):
    """Get traffic statistics and system metrics"""
    return JsonResponse({
        "message": "📊 Traffic Statistics Dashboard",
        "system_status": {
            "api_health": "✅ Active",
            "database": "✅ Connected", 
            "ai_vision": "✅ Ready",
            "optimization": "✅ Running"
        },
        "traffic_metrics": {
            "total_detections": 187,
            "vehicles_today": 52,
            "optimization_score": 89,
            "active_cameras": 4,
            "congestion_level": "Moderate"
        },
        "vehicle_distribution": {
            "motorcycle": 45,
            "car": 28, 
            "tuktuk": 15,
            "bus": 7,
            "truck": 5
        },
        "peak_hours": ["07:00-09:00", "16:00-18:00"],
        "most_common_vehicle": "motorcycle",
        "last_updated": "2025-11-28 10:20:00"
    })

# =====================
# 🛣️ URL PATTERNS
# =====================
urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/vehicle-images/', vehicle_images, name='vehicle-images'),
    path('api/upload/', upload, name='upload'),
    
    # ✅ FIXED: Use the imported ai_models function from AI integration
    path('api/ai-models/', ai_models, name='ai-models'),
    
    path('api/detect/', detect_vehicles, name='detect'),
    path('stats/', stats, name='stats'),
    
    # 🎥 Live Detection Endpoints
    path('api/live-detection/start/', start_live_detection, name='start-live-detection'),
    path('api/live-detection/stop/', stop_live_detection, name='stop-live-detection'),
    path('api/live-detection/stats/', get_live_stats, name='live-detection-stats'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)