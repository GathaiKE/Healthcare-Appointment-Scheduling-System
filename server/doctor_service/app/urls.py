from django.urls import path

from .views import RegisterDoctorView, LogInView, AddSpecialization

urlpatterns=[
    # Anon routes
    path('register/', RegisterDoctorView.as_view(), name='doctor-register'),
    path('login/', LogInView.as_view(), name='login'),
    
    # Protected route
    path('specializations/', AddSpecialization.as_view(), name='add-specialization')
]