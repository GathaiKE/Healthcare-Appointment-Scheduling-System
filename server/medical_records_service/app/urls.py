from django.urls import path

from .views import CreateRecordView, RecordUpdateView, TestDetailView, ListDoctorRecordsView, ListPatientRecordsView, AppointmentPatientHistoryView, RecordRetrieveView, RecordDestroyView

urlpatterns=[
    path('', CreateRecordView.as_view(),  name="create-record"),
    path('<str:pk>/', RecordRetrieveView.as_view(), name="record-retrieve"),
    path('<str:pk>/update/', RecordUpdateView.as_view(), name="record-update"),
    path('<str:pk>/delete/', RecordDestroyView.as_view(), name="record-delete"),
    path('test/<str:pk>/', TestDetailView.as_view(), name="test-detail"),
    path('doctors/records/', ListDoctorRecordsView.as_view(), name="list-doctor-records"),
    path('patients/records/', ListPatientRecordsView.as_view(), name="list-patient-records"),
    path('patient/<uuid:patient_id>/records/', AppointmentPatientHistoryView.as_view(), name="list-patient-records")
]