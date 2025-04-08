from django.urls import path

from .views import CreateAppointmentView,AppointmentStatusView, CancelAppointmentView,PatientAppointmentsView,DoctorAppointmentsView, RetrieveAppointmentView

urlpatterns=[
    path('', CreateAppointmentView.as_view(), name='set-appointment'),
    path('<str:pk>/', RetrieveAppointmentView.as_view(), name='appointment-detail'),
    path('status/<str:pk>/', AppointmentStatusView.as_view(), name="change-status"),
    path('cancel/<str:pk>/', CancelAppointmentView.as_view(), name="cancel-appointment"),
    path('patient/', PatientAppointmentsView.as_view(), name='patient-appointments'),
    path('doctor/', DoctorAppointmentsView.as_view(), name='doctor-appointments')
]