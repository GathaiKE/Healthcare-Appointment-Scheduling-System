from django.urls import path

from .views import RegisterDoctorView

url_patterns=[
    path('doctors/register/', RegisterDoctorView.as_view(), name="register-doctor")
]