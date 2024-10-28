import uuid
from autoslug import AutoSlugField
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Create your models here.
class BaseContentModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from="name", unique=True)
    image = models.ImageField()

    class Meta:
        abstract = True

    @property
    def imageUrl(self):
        try:
            return self.image.url
        except:
            return None

    def __str__(self):
        return self.name


class Category(BaseContentModel):
    image = models.ImageField(upload_to="category", blank=True)


class Brand(BaseContentModel):
    image = models.ImageField(upload_to="brands", blank=True)


class Color(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(BaseContentModel):
    GENDERS = [
        ("M", "Male"),
        ("F", "Female"),
        ("U", "Unisex"),
    ]

    image = models.ImageField(upload_to="products", verbose_name="Main Image")
    gender = models.CharField(max_length=1, choices=GENDERS)
    description = models.TextField(blank=True)
    colors = models.ManyToManyField(
        to=Color,
        related_name="products",
        blank=True,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.0"))
    in_stock = models.IntegerField(default=5)

    category = models.ForeignKey(
        to=Category,
        on_delete=models.CASCADE,
        related_name="products",
    )
    brand = models.ForeignKey(
        to=Brand,
        on_delete=models.CASCADE,
        related_name="products",
        blank=True,
        null=True,
    )

    @property
    def available_colors(self):
        return self.colors.values_list("name", flat=True)

    @property
    def default_color(self):
        return self.colors.first()

    @property
    def default_size(self):
        return self.productsizes.order_by("-quantity").first()


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to="products")
    product = models.ForeignKey(
        to=Product, on_delete=models.CASCADE, related_name="product_images"
    )

    def __str__(self):
        return self.image.name


class ProductSize(models.Model):
    PRODUCT_SIZES = (
        ("S", "SMALL"),
        ("M", "MEDIUM"),
        ("L", "LARGE"),
        ("XL", "XLARGE"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    size = models.CharField(max_length=3, choices=PRODUCT_SIZES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="productsizes"
    )

    def __str__(self):
        return f"{self.quantity} {self.get_size_display()}"


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.rating} stars"


class WishList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.product)


class ShippingAddress(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=200)

    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


class Order(models.Model):
    DELIVERY_STATUS_CHOICES = (
        ("PENDING", "PENDING"),
        ("SUCCESS", "SUCCESS"),
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_status = models.CharField(
        max_length=50, choices=DELIVERY_STATUS_CHOICES, default="PENDING"
    )

    def __str__(self):
        return f"Order for {self.user}"


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="order_items",
    )

    color = models.CharField(max_length=20, blank=True)
    size = models.CharField(max_length=3, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def clean(self):
        if self.color:
            color_valid = self.product.colors.filter(name=self.color).exists()
            if not color_valid:
                raise ValidationError(
                    {
                        "color": f"Invalid color `{self.color}` selected\
                                       for {self.product}"
                    }
                )

        if self.size:
            size_valid = self.product.productsizes.filter(size=self.size).exists()
            if not size_valid:
                raise ValidationError(
                    {
                        "color": f"Invalid size `{self.size}` selected\
                                       for {self.product}"
                    }
                )

    def save(self, **kwargs):
        if not self.color:
            self.color = self.product.default_color

        if not self.size:
            self.size = self.product.default_size

        self.full_clean()
        super.save(**kwargs)

    def __str__(self):
        return self.product
