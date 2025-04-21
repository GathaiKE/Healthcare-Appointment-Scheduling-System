from rest_framework import serializers
from datetime import datetime, timedelta

from .models import Appointment, Slot, DoctorCalender


class CreateAppointmentSeriaizer(serializers.ModelSerializer):
    doctor_id=serializers.CharField(write_only=True)
    start_time=serializers.TimeField(write_only=True)
    date=serializers.DateField(write_only=True)
    class Meta:
        model=Appointment
        fields=['id', 'doctor_id', 'patient_id', 'hospital_id', 'date', 'start_time', 'status', 'created_at', 'updated_at', 'deleted_at']
        read_only_fields=['id', 'created_at', 'status', 'updated_at', 'deleted_at']


    def doctor_is_on_call(self, doctor_id, start_time, end_time, date=date):
        doctor_shift=DoctorCalender.objects.get(id=doctor_id)
        is_weekend=datetime.combine(date, start_time).day == 5 or datetime.combine(date, start_time).day==6
        shift_start=doctor_shift.weekend_shift_start if is_weekend else doctor_shift.weekday_shift_start
        shift_end=doctor_shift.weekend_shift_end if is_weekend else doctor_shift.weekday_shift_end
        shift_break_start=doctor_shift.weekend_break_start if is_weekend else doctor_shift.weekday_break_start
        shift_break_duration=doctor_shift.weekend_break_duration if is_weekend else doctor_shift.weekday_break_duration
        shift_break_end=shift_break_start+timedelta(minutes=shift_break_duration)

        if start_time<shift_start or end_time<shift_start or end_time > shift_end:
            return False
        elif (start_time<shift_break_end and start_time>shift_break_start) or (end_time > shift_break_start and end_time<shift_break_end):
            return False
        else:
            return True


    def slot_available(self, doctor_id, date ,start_time, end_time):
        if not self.doctor_is_on_call(doctor_id=doctor_id,date=date, start_time=start_time, end_time=end_time):
            return False
        
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

            appointment=Appointment.objects.create(**validated_data, status=Appointment.Status.PENDING, slot=slot)
            return appointment
        else:
            raise serializers.ValidationError("The doctor is not available at that time")
    
    
class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model=Slot
        fields=['id', 'doctor_id', 'date', 'start_time', 'end_time']

class FetchAppointmentSeriaizer(serializers.ModelSerializer):
    status=serializers.CharField(source='get_status_display', read_only=True)
    slot=SlotSerializer(read_only=True)
    class Meta:
        model=Appointment
        fields=['id', 'patient_id', 'hospital_id', 'slot', 'status', 'created_at', 'updated_at', 'deleted_at']
        read_only_fields=['id', 'created_at', 'status', 'updated_at', 'deleted_at']

class AppointmentStatusSerializer(serializers.ModelSerializer):
    status=serializers.IntegerField(required=True)
    class Meta:
        model=Appointment
        fields=['status']