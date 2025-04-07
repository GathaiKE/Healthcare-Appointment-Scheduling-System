from django.urls import path

from .views import CreateAppointmentView,AppointmentStatusView, CancelAppointmentView,PatientAppointments,DoctorAppointments

urlpatterns=[
    path('', CreateAppointmentView.as_view(), name='set-appointment'),
    path('status/<str:pk>/', AppointmentStatusView.as_view(), name="change-status"),
    path('cancel/<str:pk>/', CancelAppointmentView.as_view(), name="cancel-appointment"),
    path('patient/', PatientAppointments.as_view(), name='patient-appointments'),
    path('doctor/', DoctorAppointments.as_view(), name='doctor-appointments')
]