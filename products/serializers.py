from rest_framework import serializers

from products.models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    """serializes a product image model obj"""
    image_url = serializers.SerializerMethodField(read_only=True)
    image = serializers.ImageField(required=False, write_only=True)

    class Meta:
        model = ProductImage
        fields = ("id", "image_url", "image", "image_code")
        read_only_fields = ("id",)

    def get_image_url(self, instance):
        """returns absolute url of image"""
        request = self.context.get("request")
        if hasattr(instance, "image"):
            image_url = instance.image.url
            return request.build_absolute_uri(image_url)
        return None

    def create(self, validated_data):
        """creates a new image details obj in DB"""
        image_code = validated_data["image_code"]
        if image_code:
            image = ProductImage.objects.filter(image_code=image_code).first()
            if image:
                error = {
                    "message": f"Product with code ({image_code}) exists"
                }
                raise serializers.ValidationError(error, code="validation")

        request = self.context.get("request")
        if request and hasattr(request, "user"):
            request_user = request.user
            validated_data.pop("request_user")
        else:
            request_user = validated_data.pop("request_user")

        validated_data["created_by"] = request_user.id
        validated_data["updated_by"] = request_user.id
        product_image = ProductImage.objects.create(**validated_data)
        if len(product_image.image_code) == 0:
            product = validated_data["product"]
            product_image.image_code = f"{product.product_code}-{product_image.id}"
            product_image.save()
        return product_image

    def update(self, instance, validated_data):
        """updates a product image instance in db with validated data"""
        image_code = validated_data["image_code"]
        if image_code:
            image = ProductImage.objects.filter(image_code=image_code).first()
            if image:
                error = {
                    "message": f"Product with code ({image_code}) exists"
                }
                raise serializers.ValidationError(error, code="validation")

        request = self.context.get("request")
        if request and hasattr(request, "user"):
            request_user = request.user
            validated_data.pop("request_user")
        else:
            request_user = validated_data.pop("request_user")

        instance.product = validated_data.get("product_id", instance.product)
        instance.image = validated_data.get("image", instance.image)
        instance.image_code = validated_data.get("image_code", instance.image_code)
        instance.is_main_image = validated_data.get("is_main_image", instance.is_main_image)
        instance.updated_on = validated_data["updated_on"]
        instance.updated_by = request_user.id
        instance.save()
        return instance


class ProductSerializer(serializers.ModelSerializer):
    """serializes product objects"""
    created_on = serializers.DateTimeField(required=False)
    updated_on = serializers.DateTimeField(required=False)

    class Meta:
        model = Product
        fields = (
            "id", "name", "product_code", "price", "cost", "is_service", "created_on", "updated_on",
            "created_by", "updated_by", "is_deleted", "is_available", "units_available", "category"
        )
        read_only_fields = ("id", "created_by", "updated_by")

    def create(self, validated_data):
        """creates a new product with validated data"""
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            request_user = request.user
        else:
            request_user = validated_data.pop("request_user")

        validated_data["created_by"] = request_user.id
        validated_data["updated_by"] = request_user.id
        validated_data["is_available"] = True
        product = Product.objects.create(**validated_data)
        return product

    def update(self, instance, validated_data):
        """updates a product obj"""
        request = self.context.get("user")
        if request and hasattr(request, "user"):
            request_user = request.user
        else:
            request_user = validated_data.pop("request_user")
        instance.name = validated_data.get("name", instance.name)
        instance.price = validated_data.get("price", instance.price)
        instance.cost = validated_data.get("cost", instance.cost)
        instance.product_code = validated_data.get("product_code", instance.product_code)
        instance.is_service = validated_data.get("is_service", instance.is_service)
        instance.updated_on = validated_data.get("updated_on", instance.updated_on)
        instance.is_deleted = validated_data.get("is_deleted", instance.is_deleted)
        instance.is_available = validated_data.get("is_available", instance.is_available)
        instance.category = validated_data.get("category", instance.category)
        instance.units_available = validated_data.get("units_available", instance.units_available)

        instance.updated_by = request_user.id
        instance.save()
        return instance
