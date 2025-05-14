from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DoctorViewSet, AdministratorViewSet, PatientViewSet, AuthenticationViewSet

router=DefaultRouter()
router.register(f'admins', AdministratorViewSet, basename='admin')
router.register(f'doctors', DoctorViewSet, basename='doctor')
router.register(f'patients', PatientViewSet, basename='patient')
router.register(f'auth', AuthenticationViewSet, basename='auth')

urlpatterns=[
    path('', include(router.urls), name="gateway-routes")
]