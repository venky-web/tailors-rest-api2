from django.urls import path

from account import views


urlpatterns = [
    path("", views.UserListView.as_view(), name="user_list"),
    path("create/", views.UserCreateView.as_view(), name="user_create"),
    path("<int:id>/", views.UserDetailView.as_view(), name="user_detail"),
]
