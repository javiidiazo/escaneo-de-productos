from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'barcode',
            'title',
            'price',
            'currency',
            'image_url',
            'description',
            'brand',
            'attributes',
            'updated_at',
        ]
