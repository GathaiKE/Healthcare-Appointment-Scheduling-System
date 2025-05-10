from api_gateway.celery import app

def register_doctor(validated_data):
    message={'action':"register_doctor",'data':validated_data}
    app.send_task("register_doctor", args=[message], queue='doctors')

def register_patient(validated_data):
    message={'action':"register_patient",'data':validated_data}
    app.send_task("register_patient", args=[message], queue='patients')


def register_admin(validated_data):
    message={'action':"register_admin",'data':validated_data}
    app.send_task("register_admin", args=[message], queue='administrator')