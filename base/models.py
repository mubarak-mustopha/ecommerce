from django.core.exceptions import ValidationError
from django.db import models

import uuid
from products.models import Product, Category


# Create your models here.
class SiteDetail(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=150, default="Zay Shop")
    email = models.EmailField(default="mubaarock021@gmail.com")
    address = models.CharField(
        max_length=300, default="123 Consectetur at ligula 10660"
    )
    phone = models.CharField(max_length=150, default="+2347014887266")

    fb = models.URLField(
        max_length=300, verbose_name="Facebook", default="https://facebook.com"
    )
    tw = models.URLField(
        max_length=300, verbose_name="Twitter", default="https://twitter.com"
    )
    ig = models.URLField(
        max_length=300, verbose_name="Instagram", default="https://instagram.com"
    )
    li = models.URLField(
        max_length=300, verbose_name="LinkedIn", default="https://linkedin.com"
    )

    featured_products = models.ManyToManyField(
        to=Product, related_name="featured_products"
    )

    cats_of_month = models.ManyToManyField(
        to=Category,
        related_name="cats_of_month",
        verbose_name="Categories of The Month",
    )

    # carousel images
    banner_img1 = models.ImageField(upload_to="assets/", default="")
    banner_img2 = models.ImageField(upload_to="assets/", default="")
    banner_img3 = models.ImageField(upload_to="assets/", default="")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self._state.adding and SiteDetail.objects.exists():
            raise ValidationError("There can only be one site detail instance")
        return super().save(*args, **kwargs)
