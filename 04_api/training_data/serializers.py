from rest_framework import serializers
from .models import VehicleImage

class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = '__all__'