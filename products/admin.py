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
    list_display = ("name", "category", "brand")
    inlines = [ProductImageInline, ProductSizeInline]


admin.site.register(Product, ProductAdmin)
admin.site.register(Color)
admin.site.register(Category)
admin.site.register(Brand)
