from django.urls import path
from .views import CartDetailView, CartItemAddView, CartItemRemoveView 

app_name = 'carts'

urlpatterns = [
    path('', CartDetailView.as_view(), name='cart-detail'),
    path('add/<int:product_id>/', CartItemAddView.as_view(), name='cart-item-add'),
    path('remove/<int:product_id>/', CartItemRemoveView.as_view(), name='cart-item-remove'),

]
