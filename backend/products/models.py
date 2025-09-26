from django.db import models


class Product(models.Model):
    barcode = models.CharField(max_length=32, primary_key=True)
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default='ARS')
    image_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=128, blank=True)
    attributes = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self) -> str:
        return f"{self.title} ({self.barcode})"
