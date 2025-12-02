import os
import django
import sys
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traffic_api.settings')
django.setup()

from training_data.models import VehicleImage
from ai_integration.models import AIModel

def populate_data():
    print("🔄 Populating sample data with correct field structure...")
    
    # Vehicle images - using actual model fields
    vehicles = [
        {
            "vehicle_type": "motorcycle", 
            "location": "Phnom Penh", 
            "is_approved": True,
            "confidence_score": 0.92
        },
        {
            "vehicle_type": "car", 
            "location": "Siem Reap", 
            "is_approved": False,
            "confidence_score": 0.87
        },
        {
            "vehicle_type": "tuktuk", 
            "location": "Phnom Penh", 
            "is_approved": True,
            "confidence_score": 0.78
        },
        {
            "vehicle_type": "bus", 
            "location": "Sihanoukville", 
            "is_approved": True,
            "confidence_score": 0.95
        },
    ]
    
    for data in vehicles:
        # Create without image field (since it's optional)
        vehicle = VehicleImage(**data)
        vehicle.save()
        print(f"✅ Created: {vehicle.vehicle_type} from {vehicle.location}")
    
    # AI models - using actual model fields  
    ai_models = [
        {
            "name": "YOLOv8 Cambodia Moto", 
            "version": "1.0.0",
            "model_type": "object_detection",
            "is_active": True,
            "accuracy": 89.5,
            "classes": "motorcycle,car,tuktuk,bus"
        },
        {
            "name": "Traffic Flow Optimizer", 
            "version": "2.1.0",
            "model_type": "optimization", 
            "is_active": False,
            "accuracy": 76.2,
            "classes": "congestion_level,vehicle_count"
        },
    ]
    
    for data in ai_models:
        # Create without model_file field (since it's optional)
        model = AIModel(**data)
        model.save()
        print(f"✅ Created: {model.name} (Accuracy: {model.accuracy}%)")
    
    print(f"\n📊 FINAL COUNTS:")
    print(f"Vehicle images: {VehicleImage.objects.count()}")
    print(f"AI models: {AIModel.objects.count()}")
    print("🎉 Sample data created successfully in PostgreSQL!")

if __name__ == "__main__":
    populate_data()