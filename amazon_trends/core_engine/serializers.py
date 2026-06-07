from rest_framework import serializers
from .models import Tendencia

class TendenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tendencia
        fields = '__all__'