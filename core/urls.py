from django.urls import path

from core import views


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("token/", views.get_access_token, name="token"),
]
