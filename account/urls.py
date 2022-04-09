from django.urls import path

from account import views


urlpatterns = [
    path("", views.customers_list, name="business-customers-list"),
    path("create/", views.UserCreateView.as_view(), name="user-create"),
    path("<int:id>/", views.UserDetailView.as_view(), name="user-detail"),
    path("profile/<int:id>/", views.UserProfileDetailView.as_view(), name="user-profile-detail"),
    path("business/create/", views.BusinessUserCreateView.as_view(), name="business-user-create"),
    path("business/<int:id>/", views.BusinessDetailView.as_view(), name="business-detail"),
    # staff routes
    path("business/staff/", views.BusinessStaffView.as_view(), name="staff-user-list"),
    path("business/staff/<int:staff_id>/", views.BusinessStaffDetailView.as_view(),
         name="staff-user-detail"),
    path("business/staff/<int:staff_id>/profile/", views.BusinessStaffProfileDetailView.as_view(),
         name="staff-user-profile-detail"),
]
