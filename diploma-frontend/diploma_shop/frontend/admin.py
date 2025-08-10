from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse

from .models import Product, Profile, Order, Category, Review, Image


# Register your models here.
@admin.action(description="Soft delete product")
def delete_product(modeladmin, request, queryset):
    queryset.update(Available=False)


@admin.action(description="Available product")
def available_product(modeladmin, request, queryset):
    queryset.update(Available=True)


class ImageInline(admin.TabularInline):
    model = Product.images.through


def delete_ob(obj):
    obj.Available = False
    obj.save()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    actions = [delete_product, available_product]
    link_select_related = ('category',)
    search_fields = ('title',)
    list_display = ('id', 'title', 'price', 'categories', 'rating', 'freeDelivery', 'limited',
                    'count', 'salePrice', 'Available', 'edit_link', 'delete_link')
    list_editable = ('price', 'count', 'freeDelivery', 'limited', 'salePrice')
    list_display_links = ('title',)
    ordering = ('id', 'title',)

    fieldsets = [
        ('Advanced', {'fields': ('title', 'price', 'category', 'rating')}),
        ('Extra info', {'classes': ('collapse',),
                        'fields': ('freeDelivery', 'limited', 'count', 'specifications',
                                   'Available', 'reviews', 'tags')}),
        ('Sale info', {'classes': ('collapse',),
                       'fields': ('salePrice', 'dateFrom', 'dateTo')})
    ]

    def edit_link(self, obj):
        return format_html('<a href="/admin/frontend/product/{}/change/">Изменить</a>', obj.id)

    def delete_link(self, obj):
        return format_html('<a href="{}" onclick="return confirm'
                           '(\'Вы уверены, что хотите удалить этот товар?\' )">Удалить</a>',
                           reverse('delete', args=[obj.pk]))

    edit_link.short_description = 'Действие'
    delete_link.short_description = 'Удалить'

    def categories(self, obj: Product):
        return obj.category.title or None


class ProductInline(admin.TabularInline):
    model = Order.basket.through


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'image_info')
    list_display_links = ('title', 'image_info')
    ordering = ('id', 'title',)

    def image_info(self, obj: Category):
        return obj.image.src


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_select_related = ('user',)
    inlines = [ProductInline]
    list_display = ('id', 'user_verbose', 'deliveryType', 'paymentType', 'totalCost', 'totalCost', 'address')
    list_editable = ('deliveryType', 'paymentType', 'totalCost', 'totalCost',)
    ordering = ('id',)

    def user_verbose(self, obj: Order):
        return obj.user.fullName


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'email', 'text', 'rate')
    list_editable = ('author', 'email', 'rate',)
    ordering = ('id',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'fullName', 'email', 'phone', 'avatar')
    list_editable = ('fullName', 'email', 'phone', 'avatar',)
    ordering = ('id',)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'src')


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'is_staff', 'is_active')

    def delete_queryset(self, request, queryset):
        queryset.update(is_active=False)

    def delete_model(self, request, obj):
        obj.is_active = False
        obj.save()


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
