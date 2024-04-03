from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
# Local imports goes here!
from .views import show_endpoints

urlpatterns = [
    path("", show_endpoints, name='show-all-available-endpoints'),


    path('admin/', admin.site.urls),
    path("api/v1/users/", include('users.urls')),
    path("api/v1/products/", include('products.urls')),
    path("api/v1/carts/", include('carts.urls')),
    path("api/v1/orders/", include('orders.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)