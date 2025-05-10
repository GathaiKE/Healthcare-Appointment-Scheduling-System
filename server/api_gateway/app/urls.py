from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DoctorViewSet, AdministratorViewSet, PatientViewSet

admin_router=DefaultRouter()
admin_router.register(f'admins', AdministratorViewSet, basename='admins')
admin_router.register()

doctor_router=DefaultRouter()
doctor_router.register(f"doctors", DoctorViewSet, basename='doctors')

patient_router=DefaultRouter()
patient_router.register(f"doctors", PatientViewSet, basename='patients')

url_patterns=[
    # doctors endpoints
    path('doctors/', include(doctor_router.urls), name="doctor-routes"),

    # administrator endpoints
    path('admins/', include(admin_router.urls), name='admin-routes'),

    #patient endpoints
    path('patients/', include(patient_router.urls), name='patient-routes')
]