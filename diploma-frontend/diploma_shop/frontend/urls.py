from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView
from .views import (ProductDetailsView,
                    ImageDetailsView,
                    PopularProductsView,
                    SingOut,
                    SingIn,
                    SingUp,
                    BannerView,
                    CategoriesView,
                    BasketView)
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = routers.DefaultRouter()
router.register(r'product', ProductDetailsView)
router.register(r'images', ImageDetailsView)
router.register(r'products/popular', PopularProductsView, basename="popular-products")
router.register(r'products/limited', PopularProductsView, basename="limited-products")
router.register(r'banners', BannerView, basename='banners')
router.register(r'basket', BasketView, basename='basket')
router.register(r"categories", CategoriesView)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),

    path('api/sign-in', SingIn.as_view()),
    path('api/sign-out', SingOut.as_view()),
    path('api/sign-up', SingUp.as_view()),

    path('', TemplateView.as_view(template_name="frontend/index.html")),
    path('about/', TemplateView.as_view(template_name="frontend/about.html")),
    path('cart/', TemplateView.as_view(template_name="frontend/cart.html")),
    path('catalog/', TemplateView.as_view(template_name="frontend/catalog.html")),
    path('catalog/<int:id>/', TemplateView.as_view(template_name="frontend/catalog.html")),
    path('history-order/', TemplateView.as_view(template_name="frontend/historyorder.html")),
    path('order-detail/<int:id>/', TemplateView.as_view(template_name="frontend/oneorder.html")),
    path('orders/<int:id>/', TemplateView.as_view(template_name="frontend/order.html")),
    path('payment/<int:id>/', TemplateView.as_view(template_name="frontend/payment.html")),
    path('payment-someone/', TemplateView.as_view(template_name="frontend/paymentsomeone.html")),
    path('product/<int:pk>/', TemplateView.as_view(template_name="frontend/product.html")),
    path('profile/', TemplateView.as_view(template_name="frontend/profile.html")),
    path('progress-payment/', TemplateView.as_view(template_name="frontend/progressPayment.html")),
    path('sale/', TemplateView.as_view(template_name="frontend/sale.html")),
    path('sign-in/', TemplateView.as_view(template_name="frontend/signIn.html")),
    path('sign-up/', TemplateView.as_view(template_name="frontend/signUp.html")),
]

if settings.DEBUG:
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
