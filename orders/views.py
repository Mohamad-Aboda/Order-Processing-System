from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import stripe
import os
from dotenv import load_dotenv
import logging

load_dotenv()
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .models import Order
from .serializers import CardInformationSerializer
from .permissions import IsOwnerOrReadOnly
from .utils import send_order_confirmation_email

logger = logging.getLogger(__name__)



SENDER_EMAIL=os.getenv("SENDER_EMAIL")
BREVO_API_KEY=os.getenv("BREVO_API_KEY")
STRIPE_SECRET_KEY=os.getenv("STRIPE_SECRET_KEY")

class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            cart = user.cart
            total_amount = Decimal(0)
            for item in cart.items.all():
                total_amount += item.quantity * item.product.price

            for item in cart.items.all():
                if item.product.stock < item.quantity:
                    error_msg = f"Insufficient stock for {item.product.name}"
                    logger.error(error_msg)
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
        except Exception as e:
            error_msg = f"Error occurred while processing order: {str(e)}"
            logger.error(error_msg)
            return Response({'error': error_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class OrderCancelView(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
            order_items = order.orderitem_set.all()
            if order.status == 'cancelled':
                logger.warning(f'Tried to cancel already cancelled order: {order.id}')
                return Response({'error': 'This order has already been canceled'}, status=status.HTTP_400_BAD_REQUEST)

            if order.status == 'paid':
                logger.error(f'Attempted to cancel paid order: {order.id}')
                return Response({'error': 'Order cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)

            # Update order status and loop through order items
            order.status = 'cancelled'
            for item in order_items:
                product = item.product
                product.stock += item.quantity
                product.save()

            order.save()
            logger.info(f'Order cancelled successfully: {order.id}')

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            logger.error('Order not found', exc_info=True)
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
            error_msg = f"Order with ID {pk} not found"
            logger.error(error_msg)
            return Response({'error': error_msg}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            error_msg = f"Error occurred while retrieving order with ID {pk}: {str(e)}"
            logger.error(error_msg)
            return Response({'error': error_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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
                logger.warning(f'Attempted to pay for already paid order: {order.id}')
                return Response({'message': 'Order is already paid'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = CardInformationSerializer(data=request.data)

            if not serializer.is_valid():
                logger.error(f'Invalid card information submitted for order: {order.id}')
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
                logger.error(f"Error sending confirmation email for order {order.id}: {e}")

            logger.info(f'Successful payment for order: {order.id}')
            response = {
                'message': "Card Payment Success",
                'status': status.HTTP_200_OK,
            }
            return Response(response, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            logger.error(f'Order with ID {pk} not found')
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'Internal server error: {str(e)}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
