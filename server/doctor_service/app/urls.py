from django.urls import path

from .views import LogInView, SpecializationView, DoctorsListView, DoctorDetailAPIView, DoctorPasswordUpdateView, ResetPasswordView, CurrentUserView, CheckEmailView

urlpatterns=[
    # Anon routes
    # path('register/', RegisterDoctorView.as_view(), name='doctor-register'),
    path('login/', LogInView.as_view(), name='login'),
    path('reset-password/<str:pk>/', ResetPasswordView.as_view(), name="reset-password"),
    path('check-email/', CheckEmailView.as_view(), name='check-email'),
    
    # Protected route
    path('specializations/', SpecializationView.as_view(), name='new-specialization'),
    path('', DoctorsListView.as_view(), name='approved-doctors'),
    path('<str:pk>/', DoctorDetailAPIView.as_view(), name="doctor-detail"),
    path('me/', CurrentUserView.as_view(), name="current-user"),
    path('me/password/', DoctorPasswordUpdateView.as_view(), name="update-password")
]