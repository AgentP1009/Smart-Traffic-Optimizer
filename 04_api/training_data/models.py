from django.db import models

class VehicleImage(models.Model):
    VEHICLE_TYPES = [
        ('motorcycle', 'Motorcycle'),
        ('tuktuk', 'Tuktuk'),
        ('bicycle', 'Bicycle'),
        ('animal_cart', 'Animal Cart'),
        ('car', 'Car'),
        ('truck', 'Truck'),
        ('bus', 'Bus'),
    ]
    
    image = models.ImageField(upload_to='training_images/')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    location = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    confidence_score = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"{self.vehicle_type} - {self.timestamp}"

class TrainingSession(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('training', 'Training'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.status}"  