from django.contrib import admin
from .models import AIModel, DetectionJob, ModelPerformance

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'model_type', 'is_active', 'accuracy', 'created_at']
    list_filter = ['model_type', 'is_active', 'created_at']
    search_fields = ['name', 'version']

@admin.register(DetectionJob)
class DetectionJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'model_used', 'status', 'created_at', 'processing_time']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'processing_time']

@admin.register(ModelPerformance)
class ModelPerformanceAdmin(admin.ModelAdmin):
    list_display = ['model', 'precision', 'recall', 'f1_score', 'inference_speed', 'evaluated_at']
    list_filter = ['evaluated_at']