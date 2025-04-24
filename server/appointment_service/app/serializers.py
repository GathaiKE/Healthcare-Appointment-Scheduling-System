from rest_framework import serializers
from datetime import datetime, timedelta

from .models import Appointment, Slot, DoctorCalender, OffPeriod


class CreateAppointmentSeriaizer(serializers.ModelSerializer):
    doctor_id=serializers.CharField(write_only=True)
    start_time=serializers.TimeField(write_only=True)
    date=serializers.DateField(write_only=True)
    class Meta:
        model=Appointment
        fields=['id', 'doctor_id', 'patient_id', 'date', 'start_time', 'status', 'created_at', 'updated_at', 'deleted_at']
        read_only_fields=['id', 'created_at', 'status', 'updated_at', 'deleted_at']


    def doctor_is_on_call(self, doctor_id, start_time, end_time, date=date):
        doctor_shift=DoctorCalender.objects.get(doctor_id=doctor_id)
        is_weekend=datetime.combine(date, start_time).day == 5 or datetime.combine(date, start_time).day==6
        shift_start=doctor_shift.weekend_shift_start if is_weekend else doctor_shift.weekday_shift_start
        shift_end=doctor_shift.weekend_shift_end if is_weekend else doctor_shift.weekday_shift_end
        shift_break_start=doctor_shift.weekend_break_start if is_weekend else doctor_shift.weekday_break_start
        shift_break_duration=doctor_shift.weekend_break_duration if is_weekend else doctor_shift.weekday_break_duration
        shift_break_end=(datetime.combine(date,shift_break_start)+timedelta(minutes=shift_break_duration)).time()

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
    
    def doctor_is_on_leave(self, doctor_id, date, start_time, end_time):
        leave_days=OffPeriod.objects.filter(doctor_id=doctor_id)

        if not leave_days.exists():
            return False
        
        overlapping_days=list()

        for entry in leave_days:
            if (entry.start_date<=date and entry.end_date>=date):
                if (entry.start_time<=start_time and entry.end_time >=start_time) or (entry.start_time<=end_time and entry.end_time>=end_time):
                    overlapping_days.append(entry)
        if len(overlapping_days) > 0:
            return True
        return False

    def create(self, validated_data):
        doctor_id=validated_data.pop('doctor_id')
        start_time=validated_data.pop('start_time')
        date=validated_data.pop('date')
        start_date_time=datetime.combine(date, start_time)
        end_date_time=start_date_time+timedelta(minutes=45)
        end_time=end_date_time.time()

        if self.doctor_is_on_leave(doctor_id=doctor_id, date=date, end_time=end_time, start_time=start_time):
            raise serializers.ValidationError("Doctor will be on leave at that time")

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

class UpdateAppointmentSeriaizer(serializers.ModelSerializer):
    start_time=serializers.TimeField(write_only=True)
    date=serializers.DateField(write_only=True)
    class Meta:
        model=Appointment
        fields=['id', 'date', 'start_time', 'status', 'created_at', 'updated_at', 'deleted_at']
        read_only_fields=['id', 'created_at', 'status', 'updated_at', 'deleted_at']


    def doctor_is_on_call(self, doctor_id, start_time, end_time, date=date):
        doctor_shift=DoctorCalender.objects.get(doctor_id=doctor_id)
        is_weekend=datetime.combine(date, start_time).day == 5 or datetime.combine(date, start_time).day==6
        shift_start=doctor_shift.weekend_shift_start if is_weekend else doctor_shift.weekday_shift_start
        shift_end=doctor_shift.weekend_shift_end if is_weekend else doctor_shift.weekday_shift_end
        shift_break_start=doctor_shift.weekend_break_start if is_weekend else doctor_shift.weekday_break_start
        shift_break_duration=doctor_shift.weekend_break_duration if is_weekend else doctor_shift.weekday_break_duration
        shift_break_end=(datetime.combine(date,shift_break_start)+timedelta(minutes=shift_break_duration)).time()

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
    
    def doctor_is_on_leave(self, doctor_id, date, start_time, end_time):
        leave_days=OffPeriod.objects.filter(doctor_id=doctor_id)

        if not leave_days.exists():
            return False
        
        overlapping_days=list()

        for entry in leave_days:
            if (entry.start_date<=date and entry.end_date>=date):
                if (entry.start_time<=start_time and entry.end_time >=start_time) or (entry.start_time<=end_time and entry.end_time>=end_time):
                    overlapping_days.append(entry)
        if len(overlapping_days) > 0:
            return True
        return False

    def update(self, instance, validated_data):
        appointment_id=instance.pk
        appointment=Appointment.objects.get(id=appointment_id)
        start_time=validated_data.pop('start_time')
        date=validated_data.pop('date')
        start_date_time=datetime.combine(date, start_time)
        end_date_time=start_date_time+timedelta(minutes=45)
        end_time=end_date_time.time()
        
        if self.doctor_is_on_leave(doctor_id=appointment.slot.doctor_id, date=date, end_time=end_time, start_time=start_time):
            raise serializers.ValidationError("Doctor will be on leave at that time")

        if self.slot_available(doctor_id=appointment.slot.doctor_id, date=date, end_time=end_time, start_time=start_time):
            appointment.slot.start_time=start_time
            appointment.slot.end_time=end_time
            appointment.slot.date=date

            appointment.slot.save()

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
        fields=['id', 'patient_id', 'slot', 'status', 'created_at', 'updated_at', 'deleted_at']
        read_only_fields=['id', 'created_at', 'status', 'updated_at', 'deleted_at']

class AppointmentStatusSerializer(serializers.ModelSerializer):
    status=serializers.IntegerField(required=True)
    class Meta:
        model=Appointment
        fields=['status']

class OffCalenderSerializer(serializers.ModelSerializer):
    end_date=serializers.DateField(required=False)
    doctor_id=serializers.CharField(required=False)
    class Meta:
        model=OffPeriod
        fields=['id','doctor_id','start_date', 'end_date', 'start_time', 'end_time', 'nature','created_at','updated_at']
        read_only_fields=['id', 'created_at','updated_at']

    def period_is_available(self, doctor_id, start_date, end_date, time_from='00:00:00', time_to='23:59:59'):
        doctor_leave_instances=OffPeriod.objects.filter(doctor_id=doctor_id)
        if not doctor_leave_instances.exists():
            return True
        
        overlapping_instances=list()
        start_time=time_from
        end_time=time_to

        for instance in doctor_leave_instances:

            if (instance.start_date<=end_date and instance.end_date>=end_date) or (instance.start_date<=start_date and instance.end_date>=start_date):
                if (instance.start_time<=end_time and instance.end_time>=end_time) or (instance.start_time<=start_time and instance.end_time>=start_time):
                    overlapping_instances.append(instance)

        return not len(overlapping_instances)>0


    def create(self, validated_data):
        doctor_id=self.context['request'].user.id
        start_date=validated_data.pop('start_date', None)
        end_date=validated_data.pop('end_date', start_date)
        start_time=validated_data['start_time'] or "00:00:00"
        end_time=validated_data['end_time'] or "23:59:59"

        if not self.period_is_available(doctor_id,start_date, end_date, time_to=end_time, time_from=start_time):
            raise serializers.ValidationError("Doctor is already on leave at specified time.")
        
        entry=OffPeriod.objects.create(
            doctor_id=doctor_id,
            start_date=start_date,
            end_date=end_date,
            **validated_data
            )
        
        return entry
