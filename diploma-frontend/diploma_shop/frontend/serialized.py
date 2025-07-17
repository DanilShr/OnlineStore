from rest_framework import serializers
from .models import Product, Image, Basket, Tag, Review


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['src', 'alt']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rate']

    def to_representation(self, instance):
        return instance.rate


class TagsShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']

    def to_representation(self, instance):
        return instance.name


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)
    tags = TagsShortSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'count', 'date', 'title',
                  'description', 'fullDescription', 'freeDelivery', 'images',
                  'tags', 'reviews', 'specifications', 'rating']


class ProductShortSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)
    tags = TagsSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'count', 'date', 'title',
                  'description', 'freeDelivery', 'images',
                  'tags', 'reviews', 'rating']


class BasketSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Basket
        fields = ['products']
