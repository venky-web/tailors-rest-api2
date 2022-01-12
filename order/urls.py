from django.urls import path

from order import views


urlpatterns = [
    path("", views.OrderListCreateView.as_view(), name="orders"),
    path("<int:id>/", views.OrderDetailView.as_view(), name="order_details"),
    path("<int:order_id>/items/", views.OrderItemListCreateView.as_view(), name="order_items"),
    path("<int:order_id>/items/<int:order_item_id>/", views.OrderItemDetailView.as_view(),
         name="order_item_detail"),
]
