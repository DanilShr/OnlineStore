from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import OneToOneField
from django.forms import EmailField


# Create your models here.


class Review(models.Model):
    author = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=50, blank=True)
    text = models.TextField(blank=True, max_length=200)
    rate = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class Tag(models.Model):
    name = models.CharField(max_length=10)


def user_directory_path(instance, filename):

    return "user_{0}/{1}".format(instance.id, filename)


class Image(models.Model):
    src = models.ImageField(upload_to='images/')
    alt = models.CharField(max_length=50)


class Subcategories(models.Model):
    title = models.CharField(max_length=50)
    image = models.ForeignKey(Image, blank=True, null=True, on_delete=models.CASCADE)


class Category(models.Model):
    title = models.CharField(max_length=50)
    image = models.ForeignKey(Image, blank=True, null=True, on_delete=models.CASCADE)
    subcategories = models.ManyToManyField(Subcategories, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)


class Specification(models.Model):
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)


class Product(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=200, blank=True)
    fullDescription = models.TextField(max_length=200, blank=True)
    category = models.ForeignKey(Category, blank=True, on_delete=models.CASCADE)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    count = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    freeDelivery = models.BooleanField(default=True, blank=True, null=True)
    limited = models.BooleanField(default=False, blank=True, null=True)
    Available = models.BooleanField(default=True, blank=True, null=True)
    images = models.ManyToManyField(Image, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    reviews = models.ManyToManyField(Review, blank=True)
    specifications = models.ForeignKey(Specification, blank=True, on_delete=models.CASCADE, null=True)
    rating = models.FloatField(default=0)
    salePrice = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    dateFrom = models.DateField(null=True, blank=True)
    dateTo = models.DateField(null=True, blank=True)

class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ForeignKey(Product, blank=True, on_delete=models.CASCADE, default='')
    count = models.IntegerField(default=0)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    total_price = models.DecimalField(default=0, max_digits=8, decimal_places=2)


class Profile(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE)
    fullName = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ForeignKey(Image, blank=True, null=True, on_delete=models.CASCADE)


class Order(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    deliveryType = models.CharField(max_length=50, null=True, blank=True)
    paymentType = models.CharField(max_length=50, null=True, blank=True)
    totalCost = models.DecimalField(decimal_places=1, default=0, max_digits=8)
    status = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(max_length=200, null=True, blank=True)
    products = models.ManyToManyField(Product, blank=True)


class Payment(models.Model):
    number = models.IntegerField(blank=True)
    name = models.CharField(max_length=100, blank=True)
    month = models.IntegerField(blank=True)
    year = models.IntegerField(blank=True)
    code = models.IntegerField(blank=True)
