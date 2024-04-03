from rest_framework import serializers

from .models import Product, ProductImage

class ProductListCreateSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "user", "stock", "price"]

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.first_name,
        }

    def validate_name(self, value):
        user = self.context["request"].user
        if Product.objects.filter(name=value, user=user).exists():
            raise serializers.ValidationError(
                "You already have a product with this name."
            )
        return value
    
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "price"]


    def validate_name(self, value):
        user = self.context["request"].user
        if Product.objects.filter(name=value, user=user).exists():
            raise serializers.ValidationError(
                "You already have a product with this name."
            )
        return value

class ProductRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "user", "stock", "price"]

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.first_name,
        }

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"

