from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model=Patient
        fields=['id', 'user_ref_id', 'created_at', 'deleted_at']
        read_only_fields=['id', 'created_at', 'deleted_at']

    def create(self, validated_data):
        patient=Patient.objects.create(**validated_data)
        return patient