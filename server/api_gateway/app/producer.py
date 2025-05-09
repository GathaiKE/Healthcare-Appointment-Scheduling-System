from api_gateway.celery import app

def register_doctor(validated_data):
    message={'action':"register_doctor",'data':validated_data}
    app.send_task("register_doctor", args=[message], queue='doctors')