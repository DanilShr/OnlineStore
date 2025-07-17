from django.contrib.auth.models import User
from django.views.generic import DetailView
from rest_framework.viewsets import ModelViewSet

from .models import Product, Image, Basket
from .serialized import (ProductSerializer,
                         ImageSerializer,
                         BasketSerializer)


class ProductDetailsView(ModelViewSet):
    queryset = ((Product.objects
                 .select_related('category', 'reviews', 'specifications'))
                .prefetch_related('tags', 'images'))
    serializer_class = ProductSerializer


class ImageDetailsView(ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class BasketListView(ModelViewSet):
    user = User.objects.first()
    queryset = ((Basket.objects.prefetch_related('products')
                .filter(user=user))
                .only('products'))

    serializer_class = BasketSerializer
