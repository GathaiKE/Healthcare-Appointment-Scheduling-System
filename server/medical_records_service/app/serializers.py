from rest_framework import serializers

from .models import MedicalRecord, Test

class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model=MedicalRecord
        fields=['id', 'prognosis', 'created_at','updated_at', 'deleted_at']
        read_only_fields=['id', 'created_at','updated_at', 'deleted_at']

    
class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model=Test
        fields=['id', 'name', "result", 'created_at','updated_at', 'deleted_at']
        read_only_fields=['id', 'created_at','updated_at', 'deleted_at']