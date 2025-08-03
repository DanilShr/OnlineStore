from django.contrib import admin

from .models import Product, Profile, Order, Category, Review


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    link_select_related = ('category',)
    search_fields = ('title',)
    list_display = ('id', 'title', 'price', 'rating', 'freeDelivery', 'limited',
                    'count', 'salePrice', 'Available')
    list_editable = ('price', 'count', 'freeDelivery', 'limited', 'salePrice')
    list_display_links = ('title',)


class ProductInline(admin.TabularInline):
    model = Order.products.through



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('title',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
    list_display = ('id', 'user', 'deliveryType', 'paymentType', 'totalCost', 'totalCost', 'address')
    list_editable = ('user', 'deliveryType', 'paymentType', 'totalCost', 'totalCost',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'email', 'text', 'rate')
    list_editable = ('author', 'email', 'rate',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'fullName', 'email', 'phone', 'avatar')
    list_editable = ('user', 'fullName', 'email', 'phone', 'avatar',)
