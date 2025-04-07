from rest_framework import serializers
from datetime import datetime, timedelta

from .models import Appointment, Slot


class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model=Slot
        fields=['id', 'doctor_id', 'date', 'start_time', 'end_time']

class AppointmentSeriaizer(serializers.ModelSerializer):
    status=serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    slot=SlotSerializer(read_only=True)
    class Meta:
        model=Appointment
        fields=['id', 'patient_id', 'hospital_id', 'slot', 'status', 'created_at', 'updated_at', 'deleted_at']
        read_only_fields=['id', 'created_at', 'status', 'updated_at', 'deleted_at']

    def slot_available(self, doctor_id, date ,start_time, end_time):
        overlapping_slots=Slot.objects.filter(
            doctor_id=doctor_id,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        return not overlapping_slots.exists()


    def create(self, validated_data):
        doctor_id=validated_data.pop('doctor_id')
        start_time=validated_data.pop('start_time')
        date=validated_data.pop('date')
        start_date_time=datetime.combine(date, start_time)
        end_date_time=start_date_time+timedelta(minutes=45)
        end_time=end_date_time.time()

        if self.slot_available(doctor_id=doctor_id, date=date, end_time=end_time, start_time=start_time):
            slot=Slot.objects.create(
                doctor_id=doctor_id,
                start_time=start_time,
                end_time=end_time,
                date=date
            )

            appointment=Appointment.objects.create(
                patient_id=validated_data['patient_id'],
                status=0,
                slot=slot
            )
            return appointment
        else:
            raise serializers.ValidationError("The suggested time overlaps with an existing booking")

class AppointmentStatusSerializer(serializers.ModelSerializer):
    status=serializers.IntegerField(required=True)
    class Meta:
        model=Appointment
        fields=['status']