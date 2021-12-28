from django.urls import path, include

from rest_framework.routers import DefaultRouter

from order import views

router = DefaultRouter()
router.register("order-items", views.OrderItemViewSet, basename="order-item")

urlpatterns = [
    # path("", include(router.urls)),
    path("", views.OrderListCreateView.as_view(), name="orders"),
    path("<int:id>/", views.OrderUpdateDeleteView.as_view(), name="order_details"),
]
