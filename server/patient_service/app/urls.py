from django.urls import path

from .views import CreatePatientView

urlpatterns=[
    path('', CreatePatientView.as_view(), name='create-patient')
]