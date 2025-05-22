from django.urls import path

from .views import CurrentUserView, AuthenticateView, PasswordUpdateView,PatientsListView, PatientDetailView, PatientActiveStatusView, PatientSelfUpdateView,CheckUniqueDetailsView, ResetPasswordView,MinorPatientView

urlpatterns=[
    # Public Endpoints
    path("login/", AuthenticateView.as_view(), name="patient-login"),
    path('details-available/', CheckUniqueDetailsView.as_view(), name='verify-unique-details'),
    path('reset-password/<str:pk>/', ResetPasswordView.as_view(), name="reset-password"),

    # Authenticated endpoints
    path("me/", CurrentUserView.as_view(), name="current-patient"),
    path("me/password/", PasswordUpdateView.as_view(), name="reset-password"),
    path("", PatientsListView.as_view(), name="users-list"),
    path("<str:pk>/", PatientDetailView.as_view(), name="users-detail"),
    path("self/update/", PatientSelfUpdateView.as_view(), name="update-patient"),
    path("status/<str:pk>/", PatientActiveStatusView.as_view(), name="user-status"),
    path('minors/register/', MinorPatientView.as_view(), name='register-minor')
]