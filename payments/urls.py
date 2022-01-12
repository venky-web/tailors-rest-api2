from django.urls import path

from payments import views

urlpatterns = [
    path("", views.PaymentListCreateView.as_view(), name="payments"),
    path("<int:payment_id>/", views.PaymentDetailView.as_view(), name="payment_detail"),
]
