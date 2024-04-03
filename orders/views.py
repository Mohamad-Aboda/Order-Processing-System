from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import stripe
import os
from dotenv import load_dotenv

load_dotenv()
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .models import Order
from .serializers import CardInformationSerializer
from .permissions import IsOwnerOrReadOnly
from .utils import send_order_confirmation_email






SENDER_EMAIL=os.getenv("SENDER_EMAIL")
BREVO_API_KEY=os.getenv("BREVO_API_KEY")
STRIPE_SECRET_KEY=os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY=os.getenv("STRIPE_PUBLISHABLE_KEY")

class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart = user.cart
        total_amount = Decimal(0)
        for item in cart.items.all():
            total_amount += item.quantity * item.product.price

        for item in cart.items.all():
            if item.product.stock < item.quantity:
                return Response({'error': f"Insufficient stock for {item.product.name}"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=user, cart=cart, total_amount=total_amount, status='pending'
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order, product=item.product, quantity=item.quantity, price=item.product.price
            )
        cart.items.all().delete()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderCancelView(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
            if order.status == 'cancelled':
                return Response({'error': 'This order has already been canceled'}, status=status.HTTP_400_BAD_REQUEST)

            if order.status == 'paid':
                return Response({'error': 'Order cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
            
            order.status = 'cancelled'
            order.save()

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            self.check_object_permissions(request, order)  # Optional permission check
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)




class UserOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class PaymentView(APIView):
    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
            if order.status == 'paid':
                return Response({'message': 'Order is already paid'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = CardInformationSerializer(data=request.data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            stripe.api_key = STRIPE_SECRET_KEY

            # Create a payment intent with test data
            payment_intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),
                currency='usd',
                payment_method_types=['card'],
            )

            # Simulate successful payment just to make things simple 
            # but before mark status as paid i should validate the client side
            order.status = 'paid'
            order.save()

            try:
                send_order_confirmation_email(SENDER_EMAIL, order.user.email, BREVO_API_KEY, order)
            except Exception as e:
                print(f"Error sending confirmation email: {e}")

            response = {
                'message': "Card Payment Success",
                'status': status.HTTP_200_OK,
            }
            return Response(response, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
