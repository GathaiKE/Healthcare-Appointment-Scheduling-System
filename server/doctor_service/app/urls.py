from django.urls import path

from .views import RegisterDoctorView, LogInView, SpecializationView, DoctorsListView, DoctorDetailAPIView, DoctorPasswordUpdateView, ResetPasswordView, CurrentUserView, CancelledDoctorsListView, SuspendedDoctorsListView, DisapprovedDoctorsListView, PendingDoctorsListView

urlpatterns=[
    # Anon routes
    path('register/', RegisterDoctorView.as_view(), name='doctor-register'),
    path('login/', LogInView.as_view(), name='login'),
    path('reset-password/<str:pk>/', ResetPasswordView.as_view(), name="reset-password"),
    
    # Protected route
    path('specializations/', SpecializationView.as_view(), name='new-specialization'),
    path('', DoctorsListView.as_view(), name='approved-doctors'),
    path('cancelled/', CancelledDoctorsListView.as_view(), name='cancelled-doctors'),
    path('suspended/', SuspendedDoctorsListView.as_view(), name='suspended-doctors'),
    path('disapproved/', DisapprovedDoctorsListView.as_view(), name='disapproves-users'),
    path('pending/', PendingDoctorsListView.as_view(), name='pending-approval-doctors'),
    path('<str:pk>/', DoctorDetailAPIView.as_view(), name="doctor-detail"),
    path('me/', CurrentUserView.as_view(), name="current-user"),
    path('me/password/', DoctorPasswordUpdateView.as_view(), name="update-password")
]