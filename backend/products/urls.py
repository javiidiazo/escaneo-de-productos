from django.urls import path

from . import views

urlpatterns = [
    path('health', views.health, name='health'),
    path('products/<str:barcode>', views.product_by_barcode, name='product-by-barcode'),
]
