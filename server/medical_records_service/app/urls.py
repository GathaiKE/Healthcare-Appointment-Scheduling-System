from django.urls import path

from .views import CreateRecordView, RecordUpdateView, TestDetailView, ListDoctorRecords

urlpatterns=[
    path('', CreateRecordView.as_view(),  name="create-record"),
    path('<str:pk>/', RecordUpdateView.as_view(), name="record-update"),
    path('test/<str:pk>/', TestDetailView.as_view(), name="test-detail"),
    path('doctor/', ListDoctorRecords.as_view(), name="list-doctor-records")
]