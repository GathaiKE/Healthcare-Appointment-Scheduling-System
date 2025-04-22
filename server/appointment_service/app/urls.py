from django.urls import path

from .views import CreateAppointmentView,AppointmentStatusView, CancelAppointmentView,PatientAppointmentsView,DoctorAppointmentsView, RetrieveAppointmentView, CreateOffCalenderView, FetchOffCalenderView, OffCalenderUpdateView, OffCalenderDestroyView, OffCalenderRetrieveView,RescheduleAppointmentView

urlpatterns=[
    path('', CreateAppointmentView.as_view(), name='set-appointment'),
    path('<str:pk>/', RetrieveAppointmentView.as_view(), name='appointment-detail'),
    path('status/<str:pk>/', AppointmentStatusView.as_view(), name="change-status"),
    path('cancel/<str:pk>/', CancelAppointmentView.as_view(), name="cancel-appointment"),
    path('<str:pk>/reschedule/', RescheduleAppointmentView.as_view(), name='reschedule-appointment'),
    path('patient/me/', PatientAppointmentsView.as_view(), name='fetch-patient-appointments'),
    path('doctor/me/', DoctorAppointmentsView.as_view(), name='fetch-doctor-appointments'),
    path('doctor/leave-period/', CreateOffCalenderView.as_view(), name='create-off-entry'),
    path('doctor/leave-period/me/', FetchOffCalenderView.as_view(), name='list-off-entries'),
    path('doctor/leave-period/<str:pk>/update/', OffCalenderUpdateView.as_view(), name='reschedule-entry'),
    path('doctor/leave-period/<str:pk>/', OffCalenderRetrieveView.as_view(), name='retrieve-off-entry'),
    path('doctor/leave-period/<str:pk>/delete/', OffCalenderDestroyView.as_view(), name='delete-off-entry')
]