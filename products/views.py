from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, Case, Value, When
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect

from .models import Product, Category, WishList, OrderItem, Order, ProductSize
from .utils import get_user_or_guest_id

from pprint import pprint as pp


# Create your views here.
def shop(request):
    top_cats = Category.objects.annotate(Count("products")).order_by("-products__count")
    products = Product.objects.prefetch_related("productsizes")

    paginator = Paginator(products, 2)
    page_num = request.GET.get("page", 1)
    products = paginator.get_page(page_num).object_list
    page_range = paginator.page_range

    user, guest_id = get_user_or_guest_id(request)
    cart, created = Order.objects.get_or_create(
        user=user,
        guest_id=guest_id,
        status="PENDING"
    )
    cart = cart.orderitems.values_list("product_id", flat=True)

    wishlist = WishList.objects.filter(user=user, guest_id=guest_id).values_list(
        "product_id", flat=True
    )

    wishlist_clause = When(
        id__in=wishlist,
        then=Value(True),
    )
    cart_clause = When(
        id__in=cart,
        then=Value(True),
    )

    products = products.annotate(
        in_wishlist=Case(
            wishlist_clause,
            default=Value(False),
        ),
        in_cart=Case(
            cart_clause,
            default=Value(False),
        ),
    )
    pp(products.values("name", "in_cart", "in_wishlist"))
    context = {
        "categories": Category.objects.values_list("name", flat=True),
        "products": products,
        "page_range": page_range,
        "current_page": int(page_num),
    }

    return render(request, "products/shop.html", context)


def toggle_wishlist(request, pk):
    product = get_object_or_404(Product, id=pk)

    user, guest_id = get_user_or_guest_id(request)
    wishlist, created = WishList.objects.get_or_create(
        user=user, guest_id=guest_id, product=product
    )
    if not created:
        wishlist.delete()
    return JsonResponse({"success": True})


def wishlist_page(request):
    user, guest_id = get_user_or_guest_id(request)
    wishlist = WishList.objects.filter(user=user, guest_id=guest_id).values_list(
        "product_id", flat=True
    )

    products = Product.objects.filter(id__in=wishlist).annotate(in_wishlist=Value(True))

    return render(request, "products/wishlist.html", {"products": products})


def cart_update(request, pk):
    action = request.GET.get("action")

    if action == "add":
        return add_item(request, pk)

    if action == "remove":
        return remove_item(request, pk)

    elif action == "increment":
        return increment_item(request, pk)

    elif action == "decrement":
        return decrement_item(request, pk)


def add_item(request, pk):
    user, guest_id = get_user_or_guest_id(request)
    product = get_object_or_404(Product, id=pk)

    order, _ = Order.objects.get_or_create(
        user=user, guest_id=guest_id, status="PENDING"
    )
    orderitem, created = OrderItem.objects.get_or_create(product=product, order=order)

    orderitems_count = len(order)

    if created:
        return JsonResponse(
            {"success": True, "cart_count": orderitems_count}, status=200
        )


def increment_item(request, pk):
    user, guest_id = get_user_or_guest_id(request)
    product = get_object_or_404(Product, id=pk)

    order = Order.objects.get(user=user, guest_id=guest_id, status="PENDING")
    orderitem = get_object_or_404(OrderItem, product=product, order=order)
    finished = False

    if size := orderitem.size:
        prod_instock = orderitem.product.productsizes.get(size=size).quantity
    else:
        prod_instock = orderitem.product.in_stock

    if prod_instock >= (orderitem.quantity + 1):
        orderitem.quantity += 1
        orderitem.save()

        if prod_instock == orderitem.quantity:
            finished = True

        subtotal = order.cart_total

        return JsonResponse(
            {
                "count": orderitem.quantity,
                "total_price": orderitem.total_price,
                "subtotal": subtotal,
                "shipping": settings.SHIPPING_PRICE,
                "total": subtotal + settings.SHIPPING_PRICE,
                "finished": finished,
            }
        )
    else:
        return JsonResponse({"error": f"{orderitem.product} out of stock"}, status=400)


def decrement_item(request, pk):
    user, guest_id = get_user_or_guest_id(request)
    product = get_object_or_404(Product, id=pk)

    order = Order.objects.get(user=user, guest_id=guest_id, status="PENDING")
    orderitem = get_object_or_404(OrderItem, product=product, order=order)

    orderitem.quantity -= 1
    if orderitem.quantity > 0:
        orderitem.save()

        subtotal = order.cart_total

        return JsonResponse(
            {
                "count": orderitem.quantity,
                "total_price": orderitem.total_price,
                "subtotal": subtotal,
                "shipping": settings.SHIPPING_PRICE,
                "total": subtotal + settings.SHIPPING_PRICE,
            }
        )
    else:
        return JsonResponse({"error": f"Orderitem can't have zero count."}, status=400)


def remove_item(request, pk):
    user, guest_id = get_user_or_guest_id(request)
    product = get_object_or_404(Product, id=pk)

    order = Order.objects.get(user=user, guest_id=guest_id, status="PENDING")
    orderitem, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
    )

    orderitem.delete()

    subtotal = order.cart_total

    return JsonResponse(
        {
            "deleted": True,
            "subtotal": subtotal,
            "shipping": settings.SHIPPING_PRICE,
            "total": subtotal + settings.SHIPPING_PRICE,
        }
    )


def cart_view(request):
    user, guest_id = get_user_or_guest_id(request)
    order = Order.objects.filter(user=user, guest_id=guest_id, status="PENDING").first()

    subtotal = order.cart_total

    return render(
        request,
        "products/cart.html",
        {
            "cart": order,
            "subtotal": subtotal,
            "shipping": settings.SHIPPING_PRICE,
            "total": subtotal + settings.SHIPPING_PRICE,
        },
    )
