from rest_framework import serializers
from django.utils import timezone

from .models import MedicalRecord, Test, RecordOwnership
    
class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model=Test
        fields=['id', 'name', 'result', 'details', 'created_at','updated_at', 'deleted_at']
        read_only_fields=['id', 'created_at','updated_at', 'deleted_at']

class RecordSerializer(serializers.ModelSerializer):
    tests=TestSerializer(required=False, many=True)
    patient_id=serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model=MedicalRecord
        fields=['id', 'prognosis', 'tests', 'age', 'height_cm', 'weight_kg', 'hiv_status', 'blood_group', 'body_temperature', 'systolic_bp', 'diastolic_bp', 'patient_id', 'created_at','updated_at', 'deleted_at']
        read_only_fields=['id', 'created_at','updated_at', 'deleted_at']

    def create(self, validated_data):
        tests_data=validated_data.pop("tests", [])
        doctor=self.context['request'].user
        patient_ref_id=validated_data.pop("patient_id", None)

        medical_record=MedicalRecord.objects.create(**validated_data)

        for test_data in tests_data:
            test=Test.objects.create(**test_data)
            medical_record.tests.add(test)

        RecordOwnership.objects.create(
            record=medical_record,
            patient_id=patient_ref_id,
            doctor_id=doctor.id
        )

        return medical_record
    
    def delete(self):
        pk=self.context['pk']
        print(f'PRIMARY KEY: {pk}')
        instance=MedicalRecord.objects.find(id=pk)
        instance.deleted_at=timezone.now()
        instance.save()
        return instance


    def update(self, instance, validated_data):
        tests_data=validated_data.pop("tests", [])
        instance.blood_group=validated_data.pop("blood_group", None)
        instance.hiv_status=validated_data.pop("hiv_status", None)
        if instance.hiv_status or instance.blood_group:
            pass

        instance.prognosis=validated_data.get("prognosis", instance.prognosis)
        instance.details=validated_data.get("details", instance.details)
        instance.age=validated_data.get("age", instance.age)
        instance.height_cm=validated_data.get("height_cm", instance.height_cm)
        instance.weight_kg=validated_data.get("weight_kg", instance.weight_kg)
        instance.save()

        for test_data in tests_data:
            test=Test.objects.create(**test_data)
            instance.tests.add(test)

        return instance
    

class RecordUpdateSerializer(serializers.ModelSerializer):
    tests=TestSerializer(required=False, many=True)
    patient_id=serializers.UUIDField(write_only=True, required=False)
    age=serializers.IntegerField(required=False)
    weight_kg=serializers.IntegerField(required=False)
    height_cm=serializers.IntegerField(required=False)
    body_temperature=serializers.IntegerField(required=False)
    blood_group=serializers.IntegerField(required=False, read_only=True)
    hiv_status=serializers.IntegerField(required=False, read_only=True)

    class Meta:
        model=MedicalRecord
        fields=['id', 'prognosis', 'tests', 'age', 'height_cm', 'weight_kg', 'hiv_status', 'blood_group', 'body_temperature', 'systolic_bp', 'diastolic_bp', 'patient_id', 'created_at','updated_at', 'deleted_at']
        read_only_fields=['id', 'created_at','updated_at', 'deleted_at']

    def update(self, instance, validated_data):
        tests_data=validated_data.pop("tests", [])
        blood_group=validated_data.pop("blood_group", None)
        hiv_status=validated_data.pop("hiv_status", None)
        if hiv_status or blood_group:
            pass

        instance.prognosis=validated_data.get("prognosis", instance.prognosis)
        instance.age=validated_data.get("age", instance.age)
        instance.height_cm=validated_data.get("height_cm", instance.height_cm)
        instance.weight_kg=validated_data.get("weight_kg", instance.weight_kg)
        instance.body_temperature=validated_data.get("body_temperature", instance.body_temperature)
        instance.save()

        for test_data in tests_data:
            test=Test.objects.create(**test_data)
            instance.tests.add(test)

        return instance
    
class RecordOwnershipSerializer(serializers.ModelSerializer):
    tests=TestSerializer(read_only=True, many=True)
    patient_id=serializers.SerializerMethodField()
    doctor_id=serializers.SerializerMethodField()
    hiv_status=serializers.CharField(source='get_hiv_status_display')
    blood_group=serializers.CharField(source='get_blood_group_display')
    class Meta:
        model=MedicalRecord
        fields=['id', 'patient_id', 'doctor_id', 'prognosis',  'age', 'height_cm', 'weight_kg', 'hiv_status', 'blood_group', 'body_temperature', 'systolic_bp', 'diastolic_bp', 'created_at','updated_at', 'deleted_at', 'tests']
        read_only_fields=['id', 'created_at','updated_at', 'deleted_at']

    def get_doctor_id(self, obj):
        ownership=getattr(obj, 'prefetched_ownership', [])
        return ownership[0].doctor_id if ownership else None
        
    def get_patient_id(self, obj):
        ownership=getattr(obj, 'prefetched_ownership', None)
        return ownership[0].patient_id if ownership else None