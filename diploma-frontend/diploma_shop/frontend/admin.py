from django.contrib import admin

from .models import Product, Profile, Order, Category, Review, Image


# Register your models here.
@admin.action(description="Soft delete product")
def delete_product(modeladmin, request, queryset):
    queryset.update(Available=False)


@admin.action(description="Available product")
def available_product(modeladmin, request, queryset):
    queryset.update(Available=True)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    actions = [delete_product, available_product]
    link_select_related = ('category',)
    search_fields = ('title',)
    list_display = ('id', 'title', 'price', 'categories', 'rating', 'freeDelivery', 'limited',
                    'count', 'salePrice', 'Available')
    list_editable = ('price', 'count', 'freeDelivery', 'limited', 'salePrice')
    list_display_links = ('title',)
    ordering = ('id', 'title',)

    def categories(self, obj: Product):
        return obj.category.title or None


class ProductInline(admin.TabularInline):
    model = Order.products.through


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('title',)
    ordering = ('id', 'title',)


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
