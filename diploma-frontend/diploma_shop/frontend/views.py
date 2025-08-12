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
        basket = Basket.objects.prefetch_related('item').filter(user=user.id).first()
        if basket:
            products = self.get_basket_item(basket)
            return JsonResponse(products, status=200, safe=False)
        return HttpResponse(status=200)

    def post(self, request):
        user = request.user
        basket, create = Basket.objects.update_or_create(user=user.id,
                                                         defaults={
                                                             'user': user,
                                                         })
        data = request.data
        product = Product.objects.get(id=data['id'])
        product.count -= data['count']
        product.save()
        items = CartItem.objects.filter(product=product, basket=basket)
        if items:
            item = items.first()
            item.count += int(data['count'])
            item.save()
        else:
            item = CartItem.objects.create(count=data['count'], product=product)
            basket.item.add(item)

        products = self.get_basket_item(basket)

        return JsonResponse(products, status=200, safe=False)

    def delete(self, request):
        user = request.user
        data = request.data
        basket = Basket.objects.prefetch_related('item').get(user=user)
        item = CartItem.objects.get(basket=basket, product=data['id'])
        product = Product.objects.get(id=data['id'])
        if item.count - data['count'] > 0:
            item.count -= data['count']
            item.save()
        else:
            item.delete()
        product.count += data['count']
        product.save()

        products = self.get_basket_item(basket)

        return JsonResponse(products, status=200, safe=False)

    def get_basket_item(self, basket):
        items = basket.item.all()
        products = [i.product for i in items]
        serializer = ProductShortSerializer(products, many=True)
        products = serializer.data
        for p in products:
            count = (CartItem.objects
                     .only('count')
                     .get(product=p['id'], basket=basket))
            p['count'] = count.count
        return products


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
            src=image.get('src'),
            alt=image.get('alt')
        )
        profile, created = Profile.objects.update_or_create(
            user=user,
            defaults={
                'fullName': profile.get('fullName'),
                'phone': profile.get('phone'),
                'email': profile.get('email'),
                'avatar': avatar
            }
        )
        profile_data = ProfileSerialized(profile)
        return JsonResponse(profile_data.data, safe=False, status=200)


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
        user = request.user
        profile = Profile.objects.get(user=user)
        if pk is None:
            orders = Order.objects.prefetch_related('item').filter(user=profile)
            serializer_order = OrderSerializer(orders, many=True)
            order_list = serializer_order.data
            for num in range(len(orders) - 1):
                products = [i.product for i in orders[num].item.all()]
                serializer_products = ProductShortSerializer(products, many=True)
                order_list[num]['products'] = serializer_products.data
            return JsonResponse(serializer_order.data, safe=False, status=200)
        else:
            order = (Order.objects
                     .prefetch_related('item')
                     .select_related('user')
                     .get(id=pk))
            serialized_order = OrderSerializer(order)
            order_data = serialized_order.data
            products = [i.product for i in order.item.all()]
            serializer_products = ProductShortSerializer(products, many=True)
            product_list = serializer_products.data
            for product in product_list:
                item = CartItem.objects.get(product=product['id'], order=order)
                product['count'] = item.count
            order_data['products'] = product_list
            return JsonResponse(order_data, safe=False, status=200)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user = request.user
        if pk is None:
            basket = Basket.objects.get(user=user)
            items = CartItem.objects.filter(basket=basket)
            order = Order.objects.create(user=user.profile,
                                         createdAt=datetime.datetime.now(),
                                         paymentType='not selected',
                                         deliveryType='not selected',
                                         status='being issued',
                                         totalCost=0)
            order.item.add(*items)
            return JsonResponse({'orderId': order.id}, status=200)
        else:
            total_price = 0
            user = request.user
            order_data = request.data
            order = Order.objects.filter(pk=pk)
            basket = Basket.objects.filter(user=user)
            if basket:
                basket.firts().delete()
            items = CartItem.objects.select_related('product').filter(order=order.first())
            for item in items:
                price = item.count * item.product.price
                total_price += price
            new_date = {
                'deliveryType': order_data['deliveryType'],
                'paymentType': order_data['paymentType'],
                'totalCost': total_price,
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
