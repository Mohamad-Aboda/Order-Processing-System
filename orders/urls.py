from django.urls import path
from .views import OrderCreateView, OrderDetailView, PaymentView, UserOrderListView, OrderCancelView

urlpatterns = [
    path('', OrderCreateView.as_view(), name='order-create'),
    path('all/', UserOrderListView.as_view(), name='user_orders'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
    path('<int:pk>/payment/', PaymentView.as_view(), name='order-payment'),

]
