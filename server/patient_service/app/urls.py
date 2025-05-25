from django.urls import path

from .views import CurrentUserView, AuthenticateView, PasswordUpdateView,PatientsListView, PatientDetailView, PatientActiveStatusView, PatientSelfUpdateView,CheckUniqueDetailsView, ResetPasswordView,DependentRegisterView,CurrentUserDependentsView, DependentDetailView

urlpatterns=[
    # Public Endpoints
    path("login/", AuthenticateView.as_view(), name="patient-login"),
    path('details-available/', CheckUniqueDetailsView.as_view(), name='verify-unique-details'),
    path('reset-password/<str:pk>/', ResetPasswordView.as_view(), name="reset-password"),

    # Authenticated endpoints
    path("me/", CurrentUserView.as_view(), name="current-patient"),
    path("me/password/", PasswordUpdateView.as_view(), name="reset-password"),
    path("me/dependents/", CurrentUserDependentsView.as_view(), name='list-user-dependents'),
    path('me/dependents/register/', DependentRegisterView.as_view(), name='register-minor'),
    path('me/dependents/detail/<str:pk>/', DependentDetailView.as_view(), name='delete-update-retrieve-minor'),
    path("", PatientsListView.as_view(), name="users-list"),
    path("<str:pk>/", PatientDetailView.as_view(), name="users-detail"),
    path("self/update/", PatientSelfUpdateView.as_view(), name="update-patient"),
    path("status/<str:pk>/", PatientActiveStatusView.as_view(), name="user-status")
]