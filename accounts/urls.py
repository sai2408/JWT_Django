from django.urls import path
from .views import register_view, login_view, refresh_view, me_view

urlpatterns = [
    path("register", register_view, name="register"),
    path("login", login_view, name="login"),
    path("refresh", refresh_view, name="refresh"),
    path("me", me_view, name="me"),
]
