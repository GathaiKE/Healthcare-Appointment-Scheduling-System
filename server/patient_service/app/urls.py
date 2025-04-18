from django.urls import path

from .views import CreatePatientView, CurrentUserView, AuthenticateView, PasswordUpdateView,PatientsListView, PatientDetailView, PatientActiveStatusView, PatientUpdateView

urlpatterns=[
    # Public Endpoinys
    path('register/', CreatePatientView.as_view(), name='create-patient'),
    path("login/", AuthenticateView.as_view(), name="patient-login"),

    # Authenticated endpoints
    path("me/", CurrentUserView.as_view(), name="current-patient"),
    path("me/password/", PasswordUpdateView.as_view(), name="reset-password"),
    path("", PatientsListView.as_view(), name="users-list"),
    path("<str:pk>/", PatientDetailView.as_view(), name="users-detail"),
    path("<str:pk>/update/", PatientUpdateView.as_view(), name="update-patient"),
    path("status/<str:pk>/", PatientActiveStatusView.as_view(), name="user-status")
]