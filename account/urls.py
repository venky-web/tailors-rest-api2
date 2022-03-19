from django.urls import path

from account import views


urlpatterns = [
    path("", views.BusinessStaffUserView.as_view(), name="user-list"),
    path("create/", views.UserCreateView.as_view(), name="user-create"),
    path("<int:id>/", views.UserDetailView.as_view(), name="user-detail"),
    path("profile/<int:id>/", views.UserProfileDetailView.as_view(), name="user-profile-detail"),
    path("business/create/", views.BusinessUserCreateView.as_view(), name="business-user-create"),
    path("business/<int:id>/", views.BusinessDetailView.as_view(), name="business-detail"),
]
