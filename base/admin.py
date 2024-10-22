from django.contrib import admin

# Register your models here.
from .models import SiteDetail

class SiteDetailAdmin(admin.ModelAdmin):
    model = SiteDetail
    list_display = ["name", "email", "address"]

admin.site.register(SiteDetail, SiteDetailAdmin)