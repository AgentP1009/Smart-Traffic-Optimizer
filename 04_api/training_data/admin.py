from django.contrib import admin
from .models import VehicleImage, TrainingSession

@admin.register(VehicleImage)
class VehicleImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle_type', 'location', 'timestamp', 'is_approved', 'confidence_score']
    list_filter = ['vehicle_type', 'is_approved', 'timestamp']
    search_fields = ['vehicle_type', 'location']

@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'created_at', 'completed_at', 'accuracy']
    list_filter = ['status', 'created_at']