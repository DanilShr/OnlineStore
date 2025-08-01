from rest_framework import serializers
from .models import (Product,
                     Image,
                     Basket,
                     Tag,
                     Review,
                     Subcategories,
                     Category,
                     Profile, Order, Payment)


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


class ReviewFullSerialized(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'



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
    reviews = ReviewFullSerialized(many=True)

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


class SubcategoriesSerializer(serializers.ModelSerializer):
    image = ProductImageSerializer()

    class Meta:
        model = Subcategories
        fields = ['id', 'title', 'image']


class CategoriesSerializer(serializers.ModelSerializer):
    image = ProductImageSerializer()
    subcategories = SubcategoriesSerializer(many=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'image', 'subcategories']


class BasketProductsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ['id', 'count']


class ProfileSerialized(serializers.ModelSerializer):
    avatar = ProductImageSerializer()

    class Meta:
        model = Profile
        fields = ['fullName', 'email', 'phone', 'avatar']


class ProfileSerializedOrder(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['fullName', 'email', 'phone']


class ProfileSerializedInput(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['fullName', 'email', 'phone', 'avatar']

    def create(self, validated_data):
        image = validated_data.pop('avatar')
        avatar, create = Image.objects.get_or_create(**image)
        profile = Profile.objects.update_or_create(**validated_data, avatar=avatar)
        return profile


class OrderSerializer(serializers.ModelSerializer):
    user = ProfileSerializedOrder()
    products = ProductShortSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'createdAt', 'user',
                  'deliveryType', 'paymentType', 'totalCost', 'status', 'city', 'address', 'products']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Достаем данные пользователя и удаляем ключ "user"
        user_data = data.pop('user', {})  # Если user=None, вернет пустой словарь

        # Добавляем поля пользователя в корень ответа
        data.update({
            "fullName": user_data.get("fullName"),
            "email": user_data.get("email"),
            "phone": user_data.get("phone"),
        })

        return data


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
