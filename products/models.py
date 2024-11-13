import uuid
from autoslug import AutoSlugField
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q


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
        return self.colors.first() or ""

    @property
    def default_size(self):
        if productsizes := self.productsizes.order_by("-quantity"):
            return productsizes.first().size
        return ""

    @staticmethod
    def get_product_price(product, size=None):
        if not size:
            return product.price
        return ProductSize.objects.get(product=product, size=size).price

    @staticmethod
    def get_available_quantity(product, size=None):
        if not size:
            return product.in_stock
        return ProductSize.objects.get(product=product, size=size).quantity


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
        blank=True,
        null=True,
    )
    guest_id = models.CharField(max_length=200, blank=True, default="")

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "guest_id", "product"],
                name="unique_wishlist_item",
            ),
            models.CheckConstraint(
                check=Q(user__isnull=True) ^ Q(guest_id=""),
                name="guest_or_user_wishlist_check",
                violation_error_message="Wishlist can either belong to a"
                "guest or a user",
            ),
        ]

    def __str__(self):
        return str(self.product)


class ShippingAddress(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shipping_address",
    )
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=200)

    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


class Order(models.Model):
    STATUS = (
        ("PENDING", "PENDING"),
        ("PROCESSING", "PROCESSING"),
        ("CONFIRMED", "CONFIRMED"),
        ("PACKING", "PACKING"),
        ("SHIPPING", "SHIPPING"),
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True,
    )
    guest_id = models.CharField(max_length=200, default="", blank=True)

    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, default="PENDING", blank=True)
    shipping_address = models.ForeignKey(
        ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(user__isnull=True) ^ Q(guest_id=""),
                name="guest_or_user_check",
                violation_error_message="Order can either have a" "guest_id or a user",
            ),
            models.UniqueConstraint(
                fields=("user", "guest_id"),
                condition=Q(status="PENDING"),
                name="unique_pending_order",
            ),
        ]

    @property
    def cart_total(self):
        return sum([orderitem.total_price for orderitem in self.orderitems.all()])

    def __str__(self):
        user = self.user or self.guest_id
        return f"{self.status.title()} order for {user}"

    def __iter__(self):
        for orderitem in self.orderitems.all():
            yield orderitem

    def __len__(self):
        return sum([orderitem.quantity for orderitem in self.orderitems.all()])


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="orderitems",
    )

    color = models.CharField(max_length=20, blank=True, default="")
    size = models.CharField(max_length=3, blank=True, default="")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "order",
                    "product",
                    "size",
                    "color",
                ],
                name="unique_product_size_color_order_orderitems",
            ),
        ]

    def clean(self):
        if self.color:
            color_valid = self.product.colors.filter(name=self.color).exists()
            if not color_valid:
                raise ValidationError(
                    {
                        "color": f"Invalid color `{self.color}` selected for {self.product}"
                    }
                )

        if self.size:
            size_valid = self.product.productsizes.filter(size=self.size).exists()
            if not size_valid:
                raise ValidationError(
                    {"color": f"Invalid size `{self.size}` selected for {self.product}"}
                )

    def save(self, **kwargs):
        if not self.color:
            self.color = self.product.default_color

        if not self.size:
            self.size = self.product.default_size

        self.full_clean()
        super().save(**kwargs)

    @property
    def price(self):
        return Product.get_product_price(self.product, self.size)

    @property
    def num_prod_instock(self):
        """Get number of products in stock for a given
        order item
        """
        return Product.get_available_quantity(self.product, self.size)

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return str(self.product)
