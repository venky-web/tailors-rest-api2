from django.urls import path

from account import views


urlpatterns = [
    path("", views.UserListView.as_view(), name="user-list"),
    path("create/", views.UserCreateView.as_view(), name="user-create"),
    path("create-business/", views.BusinessUserCreateView.as_view(), name="business-user-create"),
    path("<int:id>/", views.UserDetailView.as_view(), name="user-detail"),
]
