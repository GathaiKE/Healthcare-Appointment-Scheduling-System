from django.urls import path

from .views import RegisterUserView, AuthenticateView,  CurrentUserView, PasswordResetView, UserListView, UserDetailVeiew, UserStatusView

urlpatterns = [
    # Public endpoints
    path("register/", RegisterUserView.as_view(), name="user-register"),
    path("login/", AuthenticateView.as_view(), name="user-login"),

    # Authenticated endpoints
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("me/password/", PasswordResetView.as_view(), name="reset-password"),

    # Admin endpoints
    path("", UserListView.as_view(), name="users-list"),
    path("<str:pk>/", UserDetailVeiew.as_view(), name="users-detail"),
    path("status/<str:pk>/", UserStatusView.as_view(), name="user-status")
]