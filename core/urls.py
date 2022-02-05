from django.urls import path

from core import views


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("token/", views.get_access_token, name="token"),
    path("activate-user/", views.activate_user, name="activate-user"),
    path("activate-staff/", views.activate_staff, name="activate-staff"),
]
