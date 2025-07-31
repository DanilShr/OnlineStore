from django.contrib import admin

from .models import Product, Profile, Order, Category


# Register your models here.
@admin.register(Product, Profile, Order, Category)
class ProductAdmin(admin.ModelAdmin):
    pass
