from rest_framework import serializers
# Local Import goes here!
from .models import Cart, CartItem
from .models import Cart, CartItem
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.total_price()

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)


    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items']

