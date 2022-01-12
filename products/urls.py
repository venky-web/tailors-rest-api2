from django.urls import path

from products import views


urlpatterns = [
    path("", views.ProductListCreateView.as_view(), name="products"),
    path("<int:id>/", views.ProductDetailView().as_view(), name="product_detail"),
    path("<int:id>/uploads/", views.ProductImageView.as_view(), name="product_image"),
    path("<int:id>/uploads/<int:image_id>/", views.ProductImageDetailView.as_view(), name="image_detail"),
]
