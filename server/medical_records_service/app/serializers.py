from rest_framework import serializers

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
        fields=['id', 'prognosis', 'tests', 'age', 'height_m', 'weight_kg', 'hiv_status', 'blood_group', 'body_temperature', 'systolic_bp', 'diastolic_bp', 'patient_id', 'created_at','updated_at', 'deleted_at']
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
    
    def update(self, instance, validated_data):
        tests_data=validated_data.pop("tests", [])

        instance.prognosis=validated_data.get("prognosis", instance.prognosis)
        instance.save()

        for test_data in tests_data:
            test=Test.objects.create(**test_data)
            instance.tests.add(test)

        return instance
    
class RecordOwnershipSerializer(serializers.ModelSerializer):
    tests=TestSerializer(read_only=True, many=True)
    patient_id=serializers.SerializerMethodField()
    doctor_id=serializers.SerializerMethodField()

    class Meta:
        model=MedicalRecord
        fields=['id', 'prognosis', 'tests', 'doctor_id', 'patient_id', 'created_at','updated_at', 'deleted_at']
        read_only_fields=['id', 'created_at','updated_at', 'deleted_at']

    def get_doctor_id(self, obj):
        ownership=getattr(obj, 'prefetched_ownership', [])
        return ownership[0].doctor_id if ownership else None
        
    def get_patient_id(self, obj):
        ownership=getattr(obj, 'prefetched_ownership', None)
        return ownership[0].patient_id if ownership else None