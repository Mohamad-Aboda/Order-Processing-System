from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging

from .models import Cart, CartItem
from products.models import Product
from .serializers import CartSerializer, CartItemSerializer

from dotenv import load_dotenv
logger = logging.getLogger(__name__)
load_dotenv()





class CartDetailView(APIView):
    def get(self, request):
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f'Error occurred while retrieving cart: {str(e)}')
            return Response({'error': 'An error occurred while retrieving the cart.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class CartItemAddView(APIView):
    def post(self, request, product_id):
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                logger.error('Attempted to add non-existent product to cart')
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
        except Exception as e:
            logger.error(f'Error occurred while adding item to cart: {str(e)}')
            return Response({'error': 'An error occurred while adding item to cart.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartItemRemoveView(APIView):
    def post(self, request, product_id):
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                logger.error('Attempted to remove non-existent product from cart')
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
        except Exception as e:
            logger.error(f'Error occurred while removing item from cart: {str(e)}')
            return Response({'error': 'An error occurred while removing item from cart.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class CartDetailView(APIView):
#     def get(self, request):
#         cart, created = Cart.objects.get_or_create(user=request.user)
#         serializer = CartSerializer(cart)
#         return Response(serializer.data)

        
# class CartItemAddView(APIView):
#     def post(self, request, product_id):
#         cart, created = Cart.objects.get_or_create(user=request.user)
        
#         try:
#             product = Product.objects.get(pk=product_id)
#         except Product.DoesNotExist:
#             return Response({"error": "The product does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
#         # Check if the product is in stock
#         if product.stock > 0:
#             quantity = int(request.data.get('quantity', 1))  # Default to 1 if quantity is not specified
#             if quantity <= product.stock:
#                 # Check if the product is already in the cart
#                 if CartItem.objects.filter(cart=cart, product=product).exists():
#                     cart_item = CartItem.objects.get(cart=cart, product=product)
#                     cart_item.quantity += quantity
#                     cart_item.save()
#                 else:
#                     cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
                
#                 # Deduct the quantity from the product's stock
#                 product.stock -= quantity
#                 product.save()

#                 serializer = CartItemSerializer(cart_item)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             else:
#                 return Response({"error": "Insufficient stock for the requested quantity."}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({"error": "The product is out of stock."}, status=status.HTTP_400_BAD_REQUEST)



# class CartItemRemoveView(APIView):
#     def post(self, request, product_id):
#         cart, created = Cart.objects.get_or_create(user=request.user)
#         try:
#             product = Product.objects.get(pk=product_id)
#         except Product.DoesNotExist:
#             return Response({"error": "The product does not exist."}, status=status.HTTP_404_NOT_FOUND)

#         # Check if the product is in the cart
#         if CartItem.objects.filter(cart=cart, product=product).exists():
#             cart_item = CartItem.objects.get(cart=cart, product=product)
#             quantity = int(request.data.get('quantity', 1))  # Default to 1 if quantity is not specified
#             if quantity <= cart_item.quantity:  # Ensure that the requested quantity does not exceed the quantity in the cart
#                 cart_item.quantity -= quantity
#                 cart_item.save()

#                 # Remove the item from the cart if the quantity becomes zero
#                 if cart_item.quantity == 0:
#                     cart_item.delete()

#                 # Add the quantity back to the product's stock
#                 product.stock += quantity
#                 product.save()

#                 return Response({"message": f"{quantity} units of the product have been removed from the cart."}, status=status.HTTP_204_NO_CONTENT)
#             else:
#                 return Response({"error": "The requested quantity exceeds the quantity in the cart."}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response({"error": "The product is not in the cart."}, status=status.HTTP_400_BAD_REQUEST)


