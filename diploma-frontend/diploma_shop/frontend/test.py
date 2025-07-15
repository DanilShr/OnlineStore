from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Category(models.Model):
    pass


class Specification(models.Model):
    pass


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=50, blank=True)
    text = models.TextField(blank=True, max_length=200)
    rate = models.IntegerField(max_length=1, default=0)
    date = models.DateTimeField()


class Tag(models.Model):
    name = models.CharField(max_length=10)


class Image(models.Model):
    src = models.CharField(max_length=100)
    alt = models.CharField(max_length=100, blank=True)


class Product(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=200, blank=True)
    fullDescription = models.TextField(max_length=200, blank=True)
    category = models.ForeignKey(Category, blank=True, on_delete=models.CASCADE)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    count = models.IntegerField(max_length=10, default=0)
    date = models.DateTimeField()
    freeDelivery = models.BooleanField(default=True)
    images = models.ForeignKey(Image, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, on_delete=models.CASCADE)
    reviews = models.ForeignKey(Review, blank=True, on_delete=models.CASCADE)
    specifications = models.ForeignKey(Specification, blank=True, on_delete=models.CASCADE)
    rating = models.DecimalField(default=0)
