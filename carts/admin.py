from django.contrib import admin
# Local imports goes here!
from .models import  Cart, CartItem

admin.site.register(Cart)
admin.site.register(CartItem)
