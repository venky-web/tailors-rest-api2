from django.shortcuts import get_object_or_404

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser

from products import serializers
from products.models import Product, ProductDesignImage
from helpers import functions as f
from core.permissions import IsProductSeller


def get_product_images(product_id, main_image=False):
    """returns product main image or list of images
        args: product_id, main_image (default=False)
    """
    queryset = ProductDesignImage.objects\
        .filter(product_id=product_id)\
        .order_by("-id")\
        .only("image")
    if main_image:
        img = queryset.filter(is_main_image=True)
        if img:
            return img
        else:
            try:
                return queryset[:1]
            except:
                return None
    else:
        return queryset


class ProductListCreateView(ListCreateAPIView):
    """list and create view of product"""
    serializer_class = serializers.ProductSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def get_queryset(self):
        """returns queryset of products"""
        return Product.objects.filter(seller=self.request.user,
                                      is_deleted=False).order_by("-id")

    def list(self, request, *args, **kwargs):
        """returns list of products"""
        queryset = self.get_queryset()
        products = self.serializer_class(queryset, many=True).data
        return Response(products, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """creates a new product in the db"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        now = f.get_current_time()
        serializer.save(
            request_user=request.user,
            created_on=now,
            updated_on=now
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    """Get, update and delete product view"""
    serializer_class = serializers.ProductSerializer
    permission_classes = (IsAuthenticated, IsProductSeller)
    parser_classes = (MultiPartParser,)

    def get_queryset(self):
        """returns product queryset"""
        return Product.objects.filter(seller=self.request.user, is_deleted=False)

    def retrieve(self, request, *args, **kwargs):
        """returns a single product object"""
        queryset = self.get_queryset()
        product = get_object_or_404(queryset, pk=kwargs["id"])
        response_data = self.serializer_class(product).data
        images = get_product_images(kwargs["id"])
        response_data["images"] = serializers.ProductImageSerializer(
            images,
            many=True,
            context={"request": request}
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """updates a product obj"""
        queryset = self.get_queryset()
        product = get_object_or_404(queryset, pk=kwargs["id"])
        serializer = self.serializer_class(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            request_user=request.user,
            updated_on=f.get_current_time()
        )
        response_data = serializer.data
        images = get_product_images(kwargs["id"])
        response_data["images"] = serializers.ProductImageSerializer(
            images,
            many=True,
            context={"request": request}
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """marks a product is_deleted to true"""
        queryset = self.get_queryset()
        product = get_object_or_404(queryset, pk=kwargs["id"])
        modified_product = self.serializer_class(product).data
        modified_product["is_deleted"] = True
        serializer = self.serializer_class(product, data=modified_product, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            request_user=request.user,
            updated_on=f.get_current_time()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductImageView(ListCreateAPIView):
    """returns a list or creates a product image"""
    queryset = ProductDesignImage.objects.all()
    serializer_class = serializers.ProductImageSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def get_queryset(self):
        """returns product design images queryset"""
        return ProductDesignImage.objects.filter(product__seller=self.request.user,
                                                 product=self.kwargs["id"])

    def list(self, request, *args, **kwargs):
        """returns a list of product images"""
        get_object_or_404(Product, pk=kwargs["id"], seller=request.user, is_deleted=False)
        serializer = serializers.ProductImageSerializer(
            self.get_queryset(),
            many=True,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """creates a new product image in server"""
        product = get_object_or_404(Product,
                                    pk=kwargs["id"],
                                    seller=request.user,
                                    is_deleted=False)
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        now = f.get_current_time()
        serializer.save(
            product=product,
            request_user=request.user,
            created_on=now,
            updated_on=now
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductImageDetailView(RetrieveUpdateDestroyAPIView):
    """product image detail view to retrieve, update and destroy"""
    queryset = ProductDesignImage.objects.all()
    serializer_class = serializers.ProductImageSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def get_queryset(self):
        """returns queryset of product design images"""
        return ProductDesignImage.objects.filter(product__seller=self.request.user,
                                                 product=self.kwargs["id"])

    def retrieve(self, request, *args, **kwargs):
        """returns a product image with specified id"""
        get_object_or_404(Product, pk=kwargs["id"], is_deleted=False)
        queryset = self.get_queryset()
        product_image = queryset.filter(pk=kwargs["image_id"]).first()
        if product_image:
            serializer = self.get_serializer(product_image, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)

        error = {
            "message": "Requested obj is not found"
        }
        return Response(error, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        """updates a product image obj"""
        get_object_or_404(Product, pk=kwargs["id"], is_deleted=False)
        queryset = self.get_queryset()
        product_image = queryset.filter(pk=kwargs["image_id"]).first()
        if not product_image:
            error = {
                "message": "Requested obj is not found"
            }
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(product_image, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            request_user=request.user,
            updated_on=f.get_current_time()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """deletes a product image object in the db"""
        get_object_or_404(Product, pk=kwargs["id"], is_deleted=False)
        queryset = self.get_queryset()
        product_image = queryset.filter(pk=kwargs["image_id"]).first()
        if not product_image:
            error = {
                "message": "Requested obj is not found"
            }
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        product_image.image.delete()
        product_image.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
