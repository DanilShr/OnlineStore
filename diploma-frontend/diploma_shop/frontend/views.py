import datetime
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Sum, Avg, OuterRef
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django_filters.rest_framework import DjangoFilterBackend
from requests import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.http import HttpResponseRedirect

from django.contrib import messages

from .models import (Product,
                     Image,
                     Basket,
                     Category, Profile, Order, Review, Tag, CartItem)
from .serialized import (ProductSerializer,
                         ImageSerializer,
                         ProductShortSerializer,
                         CategoriesSerializer,
                         BasketProductsSerializer,
                         ProfileSerialized,
                         OrderSerializer, PaymentSerializer,
                         TagsSerializer, SaleProductSerializer)


class ProductDetailsView(ModelViewSet):
    queryset = ((Product.objects
                 .select_related('category', 'specifications'))
                .prefetch_related('tags', 'reviews', 'images'))
    serializer_class = ProductSerializer


class ImageDetailsView(ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class PopularProductsView(ModelViewSet):
    queryset = ((Product.objects
                 .select_related('category', 'specifications'))
                .prefetch_related('tags', 'reviews', 'images').filter(rating__gte=4.5).filter(Available=True))[:4]
    serializer_class = ProductShortSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = response.data.get("results", [])
        return response


class LimitedProductsView(ModelViewSet):
    queryset = ((Product.objects
                 .select_related('category', 'specifications'))
                .prefetch_related('tags', 'reviews', 'images').filter(limited=True))
    serializer_class = ProductShortSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = response.data.get("results", [])
        return response


class SingOut(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        logout(request)
        return status.HTTP_200_OK


class SingIn(APIView):

    def post(self, request):
        raw_data = request.body.decode('utf-8')
        data = json.loads(raw_data)
        name = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=name, password=password)
        if user:
            login(request, user)
            return HttpResponse("OK", status=200)
        else:
            return HttpResponse("NO", status=500)


@transaction.atomic
def create_user(data):
    user = User.objects.create_user(**data)
    Profile.objects.create(user=user, fullName=data['first_name'], phone='+123-456-7890')
    return user


class SingUp(APIView):
    def post(self, request):
        raw_data = request.body.decode('utf-8')
        data = json.loads(raw_data)
        try:
            data = {
                'first_name': data.get('name'),
                'username': data.get('username'),
                'password': data.get('password')
            }
            user = authenticate(username=data['username'], password=data['password'])
            if user is not None:
                return HttpResponse("No", status=500)
            else:
                create_user(data)
                return HttpResponse("OK", status=200)
        except ValueError as e:
            return HttpResponseBadRequest(f'Ошибка пустые значения {e}', status=400)


class BannerView(ModelViewSet):
    queryset = ((Product.objects
                 .select_related('category', 'specifications'))
                .prefetch_related('tags', 'images', 'reviews')[:3])
    serializer_class = ProductShortSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = response.data.get("results", [])
        return response


class CategoriesView(ModelViewSet):
    queryset = (Category.objects
                .select_related('image')
                .prefetch_related('subcategories'))
    serializer_class = CategoriesSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = response.data.get("results", [])
        return response


class BasketAddView(APIView):
    def get(self, request):
        user = request.user
        basket = Basket.objects.prefetch_related('item').get(user=user.id)
        items = basket.item.all()
        products = [i.product for i in items]
        serializer = ProductSerializer(products, many=True)
        products = serializer.data
        for product in products:
            count = (CartItem.objects
                     .only('count')
                     .get(product=product['id'], basket=basket))
            product['count'] = count.count
        print(serializer.data)
        return JsonResponse(serializer.data, safe=False, status=200)

    def post(self, request):
        print(request.data)
        form = BasketProductsSerializer(data=request.data)
        if form.is_valid():
            id = form.validated_data.get("id")
            count = form.validated_data.get("count")
            product = Product.objects.get(id=id)
            if product.count > int(count):
                basket, created = Basket.objects.get_or_create(user=request.user, products=product)
                basket.count += count
                basket.price = product.price
                basket.total_price = product.price * basket.count
                basket.save()
                product.count -= count
                product.save()
                return HttpResponse("OK", status=200)
            return HttpResponse("Error", status=500)

    def delete(self, request):
        form = BasketProductsSerializer(data=request.data)
        if form.is_valid():
            id = form.validated_data.get("id")
            count = form.validated_data.get("count")
            user = request.user
            product = Product.objects.get(id=id)
            basket = Basket.objects.get(user=user, products=product)
            if basket.count - count >= 1:
                basket.count -= count
                product.count += count
                product.save()
                basket.save()
                return HttpResponse("OK", status=200)
            else:
                Basket.delete(basket)
                product.count += count
                product.save()
                return HttpResponse("OK", status=200)


class ProfileView(APIView):

    def get(self, request):
        user = request.user
        if user:
            profile = Profile.objects.get(user=user)
            profile_data = ProfileSerialized(profile)
            return JsonResponse(profile_data.data, safe=False, status=200)

    def post(self, request):
        profile = request.data
        image = profile.pop('avatar')
        user = request.user
        avatar, create = Image.objects.get_or_create(
            src=image.get('src') or '',
            alt=image.get('alt')
        )
        profile, created = Profile.objects.update_or_create(
            user=user,
            defaults={
                'fullName': profile.get('fullName'),
                'phone': profile.get('phone'),
            }
        )
        return HttpResponse("OK", status=200)


class AvatarView(APIView):
    def post(self, request):
        file = request.FILES['avatar']
        user = request.user
        profile = Profile.objects.get(user=user)
        avatar, get = Image.objects.get_or_create(
            src=file,
            alt=file.name
        )
        profile.avatar = avatar
        profile.save()
        return HttpResponse("OK", status=200)


class PasswordView(APIView):
    def post(self, request):
        current_pass = request.data['currentPassword']
        new_pass = request.data['newPassword']
        user = request.user
        if user.check_password(current_pass):
            user.set_password(new_pass)
            user.save()
            return HttpResponse("OK", status=200)
        return HttpResponse("Wrong password", status=400)


class OrderView(APIView):

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk is None:
            user = request.user
            profile = Profile.objects.get(user=user)
            queryset = (Order.objects
                        .select_related('user')
                        .prefetch_related('basket__products')
                        .filter(user=profile.id))
            serializer = OrderSerializer(queryset, many=True)
            for order in queryset:
                print(order.basket)
            if serializer:
                return JsonResponse(serializer.data, safe=False)
            print(serializer.errors)
            return HttpResponse('NO', status=500)
        else:
            order = Order.objects.select_related('user').prefetch_related('basket').get(pk=pk)
            products_data = [basket.products for basket in order.basket.all()]
            serializer_product = ProductShortSerializer(products_data, many=True)
            products = serializer_product.data
            for product in products:
                basket = Basket.objects.get(products=product['id'])
                product['count'] = basket.count
            serializer = OrderSerializer(order)
            order = serializer.data
            order['products'] = products
            print(order)
            return JsonResponse(order, safe=False)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user = request.user
        if pk is None:
            basket = Basket.objects.filter(user=user.id).all()
            order = Order.objects.create(user=user.profile,
                                         createdAt=datetime.datetime.now(),
                                         paymentType='not selected',
                                         deliveryType='not selected',
                                         status='being issued',
                                         totalCost=0)
            order.basket.add(*basket)
            return JsonResponse({'orderId': order.id}, status=200)
        else:
            user = request.user
            order_data = request.data
            order = Order.objects.filter(pk=pk)
            basket = Basket.objects.filter(user=user.id).all()
            total_sum = basket.aggregate(total=Sum('total_price'))['total']
            basket.delete()
            new_date = {
                'deliveryType': order_data['deliveryType'],
                'paymentType': order_data['paymentType'],
                'totalCost': total_sum,
                'status': 'awaiting payment',
                'city': order_data['city'],
                'address': order_data['address']
            }

            order.update(**new_date)

            return JsonResponse({'orderId': order.first().id}, status=200)


class PaymentView(APIView):
    def post(self, request, pk):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            order = Order.objects.get(pk=pk)
            order.status = 'in transit'
            order.save()
            serializer.save()
            return HttpResponse(status=200)
        return HttpResponse(status=500)


class CatalogView(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductShortSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title']

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('filter[name]')
        minPrice = self.request.query_params.get('filter[minPrice]')
        maxPrice = self.request.query_params.get('filter[maxPrice]')
        freeDelivery = self.request.query_params.get('filter[freeDelivery]')
        available = self.request.query_params.get('filter[available]')
        category = self.request.query_params.get('category')
        sort = self.request.query_params.get('sort')
        sortType = self.request.query_params.get('sortType')
        tags = self.request.query_params.get('tags')

        sort_ord = (sort if sortType == 'dec' else f'-{sort}')
        f = {'title__contains': name,
             'price__gte': minPrice,
             'price__lte': maxPrice,
             'freeDelivery': (True if freeDelivery == 'true' else False),
             'Available': (True if available == 'true' else False),
             'category': (int(category) if category else None)}
        queryset = queryset.filter(**f).order_by(sort_ord)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(self, request, *args, **kwargs)
        response.data = response.data.get("results", [])
        response.data = {'items': response.data}
        return response


class ReviewView(APIView):
    def post(self, request, **kwargs):
        pk = kwargs['pk']
        data = request.data
        review = Review.objects.create(**data)
        print(review)
        product = Product.objects.get(id=pk)
        product.reviews.add(review)
        print(data)
        self.update_rate(product)
        return HttpResponse(status=200)

    def update_rate(self, product):
        product.rating = (Review.objects
        .filter(product=product.pk)
        .aggregate(rate=Avg('rate'))['rate'])
        product.save()


class TagsView(APIView):
    def get(self, request):
        category = self.request.query_params.get('category')
        if category is not None:
            tags = (Tag.objects.filter(category=int(category)))
            serialized = TagsSerializer(tags, many=True)
            return JsonResponse(serialized.data, safe=False)
        else:
            tags = Tag.objects.all()
            serialized = TagsSerializer(tags, many=True)
            return JsonResponse(serialized.data, safe=False)


class SaleView(APIView):
    def get(self, request):
        queryset = Product.objects.filter(salePrice__gte=1)
        print(queryset.first().salePrice)
        serialized = SaleProductSerializer(queryset, many=True)
        print(serialized.data)
        data = {'items': serialized.data}
        return JsonResponse(data, safe=False)


def delete_product(request, pk):
    product = Product.objects.get(id=pk)
    product.Available = False
    product.save()
    messages.success(request, f'Удален товар #{pk}')
    return HttpResponseRedirect('/admin/frontend/product/')
