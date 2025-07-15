from django.views.generic import DetailView
from .models import Product


class ProductDetailsView(DetailView):
    queryset = ((Product.objects
                 .select_related('category', 'images', 'reviews', 'specifications'))
                .prefetch_related('tags'))
    template_name = 'frontend/product.html'
    context_object_name = 'product'
