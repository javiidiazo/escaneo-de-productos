from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer


@api_view(['GET'])
def health(request):
    return Response({'status': 'ok'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def product_by_barcode(request, barcode: str):
    try:
        product = Product.objects.get(pk=barcode)
    except Product.DoesNotExist:
        return Response(
            {'detail': 'Producto no encontrado.', 'barcode': barcode},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = ProductSerializer(product)
    return Response(serializer.data, status=status.HTTP_200_OK)
