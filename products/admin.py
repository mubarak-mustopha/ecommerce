from django.contrib import admin

from .models import *


# Register your models here.
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 3


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ("name", "category", "brand", "in_stock")
    inlines = [ProductImageInline, ProductSizeInline]


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ("user", "guest_id", "status")


class OrderItemAdmin(admin.ModelAdmin):
    model = OrderItem
    list_display = ("order_id", "color", "size", "product", "quantity")


admin.site.register(Product, ProductAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Color)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Order, OrderAdmin)
