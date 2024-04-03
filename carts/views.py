import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated  # Optional authentication
from stripe import PaymentIntent

from .models import Cart, CartItem
from products.models import Product
from .serializers import CartSerializer, CartItemSerializer

from dotenv import load_dotenv
load_dotenv()

SENDER_EMAIL = os.getenv('SENDER_EMAIL')
BREVO_API_KEY = os.getenv('BREVO_API_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')


class CartDetailView(APIView):
    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

        
class CartItemAddView(APIView):
    def post(self, request, product_id):
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"error": "The product does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the product is in stock
        if product.stock > 0:
            quantity = int(request.data.get('quantity', 1))  # Default to 1 if quantity is not specified
            if quantity <= product.stock:
                # Check if the product is already in the cart
                if CartItem.objects.filter(cart=cart, product=product).exists():
                    cart_item = CartItem.objects.get(cart=cart, product=product)
                    cart_item.quantity += quantity
                    cart_item.save()
                else:
                    cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
                
                # Deduct the quantity from the product's stock
                product.stock -= quantity
                product.save()

                serializer = CartItemSerializer(cart_item)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Insufficient stock for the requested quantity."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "The product is out of stock."}, status=status.HTTP_400_BAD_REQUEST)



class CartItemRemoveView(APIView):
    def post(self, request, product_id):
        cart, created = Cart.objects.get_or_create(user=request.user)
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"error": "The product does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the product is in the cart
        if CartItem.objects.filter(cart=cart, product=product).exists():
            cart_item = CartItem.objects.get(cart=cart, product=product)
            quantity = int(request.data.get('quantity', 1))  # Default to 1 if quantity is not specified
            if quantity <= cart_item.quantity:  # Ensure that the requested quantity does not exceed the quantity in the cart
                cart_item.quantity -= quantity
                cart_item.save()

                # Remove the item from the cart if the quantity becomes zero
                if cart_item.quantity == 0:
                    cart_item.delete()

                # Add the quantity back to the product's stock
                product.stock += quantity
                product.save()

                return Response({"message": f"{quantity} units of the product have been removed from the cart."}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "The requested quantity exceeds the quantity in the cart."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "The product is not in the cart."}, status=status.HTTP_400_BAD_REQUEST)


