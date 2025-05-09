from doctor_service.celery import app


def create_schedue(doctor_id, **kwargs):
    app.send_task('create_doctor_calendar', args=[doctor_id], kwargs={**kwargs}, queue='appointments')

def delete_schedule(doctor_id, **kwargs):
    app.send_task('delete_doctor_calendar', args=[doctor_id], kwargs={**kwargs}, queue='appointments')

def unlink_records(doctor_id, **kwargs):
    app.send_task("unlink_doctor", args=[doctor_id], kwargs={**kwargs}, queue='medical_records')

def create_license_entry(user_id):
    app.send_task("create_license_entry", args=[user_id], queue='licensing')