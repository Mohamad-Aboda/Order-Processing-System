from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

# Local imports goes here!
from .utils import product_image_directory_path
User = get_user_model()


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return self.stock > 0

    def decrease_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False

    def increase_stock(self, quantity):
        self.stock += quantity
        self.save()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=product_image_directory_path, null=True, blank=True)

    def __str__(self):
        return self.product.name
