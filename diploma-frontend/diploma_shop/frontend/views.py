import datetime
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Q
from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.views.generic import DetailView
from requests import Response
from rest_framework import status, request
from rest_framework.mixins import CreateModelMixin
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet

from .models import (Product,
                     Image,
                     Basket,
                     Category, Profile, Order)
from .serialized import (ProductSerializer,
                         ImageSerializer,
                         ProductShortSerializer,
                         CategoriesSerializer,
                         BasketProductsSerializer,
                         ProfileSerialized,
                         ProductImageSerializer, ProfileSerializedInput, OrderSerializer)


class ProductDetailsView(ModelViewSet):
    queryset = ((Product.objects
                 .select_related('category', 'reviews', 'specifications'))
                .prefetch_related('tags', 'images'))
    serializer_class = ProductSerializer


class ImageDetailsView(ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class PopularProductsView(ModelViewSet):
    queryset = ((Product.objects
                 .select_related('category', 'reviews', 'specifications'))
                .prefetch_related('tags', 'images').filter(rating__gte=3))[:5]
    serializer_class = ProductShortSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = response.data.get("results", [])  # Оставляем только results
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


class SingUp(APIView):
    def post(self, request):
        raw_data = request.body.decode('utf-8')
        data = json.loads(raw_data)
        name = data.get('name')
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            return HttpResponse("No", status=500)
        else:
            User.objects.create_user(username=username,
                                     password=password,
                                     first_name=name,
                                     )
            return HttpResponse("OK", status=200)


class BannerView(ModelViewSet):
    queryset = ((Product.objects
                 .select_related('category', 'reviews', 'specifications'))
                .prefetch_related('tags', 'images'))
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
    def get(self, request, *args, **kwargs):
        user = request.user
        baskets = Basket.objects.select_related('products').only('products').filter(user=user)
        products = [basket.products for basket in baskets]
        for product in products:
            b = Basket.objects.only('count', 'price').get(Q(products=product) & Q(user=user))
            count = b.count
            price = b.price
            product.count = count
            product.price = price
        serialized = ProductShortSerializer(products, many=True)
        data = serialized.data
        return JsonResponse(serialized.data, safe=False, status=200)

    def post(self, request, *args, **kwargs):
        print(request.data)
        form = BasketProductsSerializer(data=request.data)
        if form.is_valid():
            id = form.validated_data.get("id")
            count = form.validated_data.get("count")
            product = Product.objects.get(id=id)
            if product.count > int(count):
                basket, created = Basket.objects.get_or_create(user=request.user, products=product)
                basket.count += count
                basket.price += product.price
                basket.save()
                product.count -= count
                product.save()
                return HttpResponse("OK", status=200)

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
            src=image.get('src'),
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


# class OrderView(APIView):
#     def get(self, request):
#         user = request.user
#         orders = (Order.objects
#                   .select_related('user')
#                   .prefetch_related('products')
#                   .filter(user=user.id))
#         print(orders)
#         serialized = OrderSerializer(orders, many=True)
#
#         return JsonResponse(serialized.data, safe=False)


class OrderView(ModelViewSet):
    queryset = (Order.objects
                .select_related('user')
                .prefetch_related('products'))
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(user=user.id)

    def post(self, request):
        user = request.user
        products = request.data
        total = 0
        for product in products:
            print(product)
            total += float(product['price']) * float(product['count'])
            print(total)
        order, create = Order.objects.update_or_create(user=user.profile,
                                                    defaults={'user': user.profile,
                                                              'createdAt': datetime.datetime.now(),
                                                              'totalCost': total})
        product_ids = [item["id"] for item in products]
        order.products.add(*product_ids)

        return HttpResponse("OK", status=500)

        #
        # for data in request.data:
        #     product = Product.objects.get(id=data['id'])
        #     order.products.add(product)
        #     order.save()
        # return HttpResponse("OK", status=200)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = response.data.get("results", [])
        return response
