from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('barcode', 'title', 'price', 'currency', 'updated_at')
    list_filter = ('currency', 'brand')
    search_fields = ('barcode', 'title', 'brand')
