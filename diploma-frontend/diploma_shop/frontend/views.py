from django.views.generic import DetailView
from .models import Product
from .serialized import ProductSerializer


class ProductDetailsView(DetailView):
    queryset = ((Product.objects
                 .select_related('category', 'images', 'reviews', 'specifications'))
                .prefetch_related('tags'))
    serializer_class = ProductSerializer
    context_object_name = 'product'
    template_name = 'frontend/product.html'
