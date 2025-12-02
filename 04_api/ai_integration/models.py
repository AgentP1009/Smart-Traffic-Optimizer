from django.db import models

class AIModel(models.Model):
    MODEL_TYPES = [
        ('yolov8n', 'YOLOv8 Nano'),
        ('yolov8s', 'YOLOv8 Small'), 
        ('yolov8m', 'YOLOv8 Medium'),
        ('custom', 'Custom Model'),
    ]
    
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20, default='1.0.0')
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    model_file = models.FileField(upload_to='ai_models/', null=True, blank=True)
    is_active = models.BooleanField(default=False)
    accuracy = models.FloatField(null=True, blank=True)
    classes = models.JSONField(default=list)  # List of class names
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} v{self.version}"

class DetectionJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    input_image = models.ImageField(upload_to='detection_inputs/')
    output_image = models.ImageField(upload_to='detection_outputs/', null=True, blank=True)
    model_used = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    results = models.JSONField(null=True, blank=True)  # Detection results
    created_at = models.DateTimeField(auto_now_add=True)
    processing_time = models.FloatField(null=True, blank=True)  # in seconds
    
    def __str__(self):
        return f"Detection {self.id} - {self.status}"

class ModelPerformance(models.Model):
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    inference_speed = models.FloatField()  # milliseconds
    evaluated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.model.name} - F1: {self.f1_score:.3f}"