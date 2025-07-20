from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=50, blank=True)
    text = models.TextField(blank=True, max_length=200)
    rate = models.IntegerField(default=0)
    date = models.DateTimeField()


class Tag(models.Model):
    name = models.CharField(max_length=10)


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
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
    images = models.ManyToManyField(Image, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    reviews = models.ForeignKey(Review, blank=True, on_delete=models.CASCADE, null=True)
    specifications = models.ForeignKey(Specification, blank=True, on_delete=models.CASCADE, null=True)
    rating = models.FloatField(default=0)


class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)
