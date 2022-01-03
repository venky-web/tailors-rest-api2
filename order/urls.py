from django.urls import path, include

from rest_framework.routers import DefaultRouter

from orders import views

router = DefaultRouter()
router.register("order-items", views.OrderItemViewSet, basename="order-item")

urlpatterns = [
    # path("", include(router.urls)),
    path("", views.OrderListCreateView.as_view(), name="orders"),
    path("<int:id>/", views.OrderDetailView.as_view(), name="order_details"),
    path("<int:order_id>/items/", views.OrderItemListCreateView.as_view(), name="order_items"),
]
