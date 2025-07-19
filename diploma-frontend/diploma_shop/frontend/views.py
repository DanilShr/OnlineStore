import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseServerError
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
                     Category)
from .serialized import (ProductSerializer,
                         ImageSerializer,
                         ProductShortSerializer,
                         CategoriesSerializer)


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

        print(data)

        name = data.get('name')
        username = data.get('username')
        password = data.get('password')
        print(name, username, password)
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


class BasketView(ModelViewSet):
    queryset = ((Product.objects
                 .select_related('category', 'reviews', 'specifications'))
                .prefetch_related('tags', 'images').filter(id=1))
    serializer_class = ProductShortSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = response.data.get("results")[0]
        return response