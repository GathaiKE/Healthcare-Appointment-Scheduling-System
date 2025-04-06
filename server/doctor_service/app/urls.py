from django.urls import path

from .views import RegisterDoctorView, LogInView, SpecializationView, DoctorsListView, DoctorDetailAPIView, DoctorPasswordUpdateView, ResetPasswordView, CurrentUserView

urlpatterns=[
    # Anon routes
    path('register/', RegisterDoctorView.as_view(), name='doctor-register'),
    path('login/', LogInView.as_view(), name='login'),
    path('reset-password/<str:pk>/', ResetPasswordView.as_view(), name="reset-password"),
    
    # Protected route
    path('specializations/', SpecializationView.as_view(), name='add-specialization'),
    path('', DoctorsListView.as_view(), name='list-doctors'),
    path('<str:pk>/', DoctorDetailAPIView.as_view(), name="doctor-detail"),
    path('me/', CurrentUserView.as_view(), name="current-user"),
    path('me/password/', DoctorPasswordUpdateView.as_view(), name="update-password")
]