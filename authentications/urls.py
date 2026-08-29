from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import login_view, me_view, register_view, user_create_view

urlpatterns = [
    # Public farmer registration.
    path("register/", register_view, name="register"),

    # Super admin-only user creation for agents and privileged accounts.
    path("users/", user_create_view, name="user-create"),

    # Authenticate user and return JWT access and refresh tokens.
    path("login/", login_view, name="login"),

    # Refresh an expired access token using the refresh token.
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Return details of the currently authenticated user.
    path("me/", me_view, name="me"),
]
