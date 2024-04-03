import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated  # Optional authentication
from stripe import PaymentIntent

# Local imports goes here!
from .models import Cart, CartItem, Product, Order
from .serializers import CartSerializer, OrderSerializer
from .utils import send_order_confirmation_email


from dotenv import load_dotenv
load_dotenv()


SENDER_EMAIL = os.getenv('SENDER_EMAIL')
BREVO_API_KEY = os.getenv('BREVO_API_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        cart, created = Cart.objects.get_or_create(user=user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        user = request.user  # Assuming authentication is in place

        try:
            # Retrieve or create the user's cart
            cart, created = Cart.objects.get_or_create(user=user)

            product_id = request.data.get('product_id')
            quantity = request.data.get('quantity')

            # Validate input data
            if not product_id or not quantity:
                return Response({'error': 'Missing product_id or quantity'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Fetch the product
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check for sufficient stock (optional, adjust based on your logic)
            if product.stock < quantity:
                return Response({'error': 'Insufficient stock for product'}, status=status.HTTP_400_BAD_REQUEST)

            # Handle adding the item to the cart
            existing_item = CartItem.objects.filter(cart=cart, product=product).first()
            if existing_item:
                # Update quantity for existing item
                existing_item.quantity += quantity
                existing_item.save()
            else:
                # Create a new CartItem
                CartItem.objects.create(cart=cart, product=product, quantity=quantity)

            cart.refresh_from_db()  # Update cart total after adding item
            serializer = CartSerializer(cart)
            return Response(serializer.data)

        except PermissionError as e:
            # Handle permission errors (e.g., user not authenticated)
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            # Catch other unexpected errors
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request, product_id=None):
        user = request.user
        cart = Cart.objects.get(user=user)

        if product_id:
            # Remove specific product from cart
            try:
                item = CartItem.objects.get(cart=cart, product=product_id)
                item.delete()
            except CartItem.DoesNotExist:
                pass  # Ignore if item doesn't exist
        else:
            # Remove all items from cart
            cart.items.clear()

        cart.refresh_from_db()  # Update cart total after removing item
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]  # Optional authentication

    def post(self, request):
        user = request.user

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        # Process cart items and calculate total amount
        order_items = []
        total_amount = 0
        for item in cart.items.all():
            product = item.product
            quantity = item.quantity

            # Validate product availability and stock
            if product.stock < quantity:
                return Response({'error': f'Insufficient stock for product {product.name}'}, status=status.HTTP_400_BAD_REQUEST)

            order_items.append({'product': product, 'quantity': quantity})
            total_amount += product.price * quantity

        # Create an Order object and related OrderItems
        order = Order.objects.create(user=user, total_amount=total_amount)
        for item in order_items:
            order.items.add(item['product'], through_defaults={'quantity': item['quantity']})

        # Simulate payment processing with Stripe (replace with real processing)
        stripe = Stripe(STRIPE_SECRET_KEY)
        try:
            payment_intent = PaymentIntent.create(
                amount=int(total_amount * 100),  # Convert to cents
                currency='usd',
                description=f'Order #{order.id}'
            )
        except Exception as e:
            order.status = 'FAILED'
            order.save()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Mark order as paid and send confirmation email (bonus)
        order.status = 'PAID'
        order.save()
        send_order_confirmation_email(SENDER_EMAIL, order.user.email, BREVO_API_KEY, order)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

