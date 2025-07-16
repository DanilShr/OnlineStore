from django.views.generic import DetailView
from rest_framework.viewsets import ModelViewSet

from .models import Product
from .serialized import ProductSerializer


class ProductDetailsView(ModelViewSet):
    queryset = ((Product.objects
                 .select_related('category', 'images', 'reviews', 'specifications'))
                .prefetch_related('tags'))
    serializer_class = ProductSerializer
