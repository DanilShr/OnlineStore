from django.views.generic import DetailView
from rest_framework.viewsets import ModelViewSet

from .models import Product, Image
from .serialized import ProductSerializer, ImageSerializer


class ProductDetailsView(ModelViewSet):
    queryset = ((Product.objects
                 .select_related('category', 'images', 'reviews', 'specifications'))
                .prefetch_related('tags'))
    serializer_class = ProductSerializer


class ImageDetailsView(ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer