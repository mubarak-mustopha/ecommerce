import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, Case, Value, When
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect

from paypal.standard.forms import PayPalPaymentsForm

from .forms import ShippingAddressForm
from .models import Product, Category, WishList, OrderItem, Order, ShippingAddress
from .utils import get_user_or_guest_id, update_product_quantity


from pprint import pprint as pp


REMOVEABLE_ORDER_STATUSES = ("PENDING", "PROCESSING")


# Create your views here.
def shop(request):
    top_cats = Category.objects.annotate(Count("products")).order_by("-products__count")
    products = Product.objects.prefetch_related("productsizes")

    paginator = Paginator(products, 2)
    page_num = request.GET.get("page", 1)
    products = paginator.get_page(page_num).object_list
    page_range = paginator.page_range

    user, guest_id = get_user_or_guest_id(request)
    cart = Order.objects.filter(user=user, guest_id=guest_id, status="PENDING").first()

    if cart:
        cart = cart.orderitems.values_list("product_id", flat=True)
    else:
        cart = []

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
    size = request.GET.get("size", "")
    color = request.GET.get("color", "")

    user, guest_id = get_user_or_guest_id(request)
    product = get_object_or_404(Product, id=pk)

    order, _ = Order.objects.get_or_create(
        user=user, guest_id=guest_id, status="PENDING"
    )

    if action == "add":
        _, created = OrderItem.objects.get_or_create(
            order=order,
            product=product,
            size=size,
            color=color,
        )
        if created:
            return JsonResponse({"success": True, "cart_count": len(order)}, status=200)

        else:
            return JsonResponse(
                {"message": "Product alreay exists in cart"}, status=400
            )

    data = {}
    orderitem = get_object_or_404(
        OrderItem, product=product, order=order, size=size, color=color
    )

    if action == "remove":
        orderitem.delete()
        data["deleted"] = True

    elif action == "increment":
        finished = False
        if item_size := orderitem.size:
            prod_instock = orderitem.product.productsizes.get(size=item_size).quantity
        else:
            prod_instock = orderitem.product.in_stock

        if prod_instock >= (orderitem.quantity + 1):
            orderitem.quantity += 1
            orderitem.save()

        if prod_instock == orderitem.quantity:
            finished = True
        data = {
            "count": orderitem.quantity,
            "total_price": orderitem.total_price,
            "finished": finished,
        }

    elif action == "decrement":
        orderitem.quantity -= 1
        if orderitem.quantity > 0:
            orderitem.save()

            data = {"count": orderitem.quantity, "total_price": orderitem.total_price}

        else:
            return JsonResponse(
                {"error": f"Orderitem can't have quantity zero."}, status=400
            )

    data["subtotal"] = order.cart_total
    data["shipping"] = settings.SHIPPING_PRICE
    data["total"] = order.cart_total + settings.SHIPPING_PRICE
    return JsonResponse(data, status=200)


def cart_view(request):
    user, guest_id = get_user_or_guest_id(request)
    order = (
        Order.objects.filter(user=user, guest_id=guest_id, status="PENDING").first()
        or []
    )

    if order:
        subtotal = order.cart_total
    else:
        subtotal = 0

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


@login_required
def orderlist_view(request):
    user = request.user
    orderlist = Order.objects.filter(user=user)
    return render(
        request,
        "products/orderlist.html",
        {
            "orderlist": orderlist,
            "removeable_order_statuses": REMOVEABLE_ORDER_STATUSES,
        },
    )


@login_required
def order_delete_view(request, order_id):
    user = request.user
    order = get_object_or_404(Order, id=order_id)
    if order.user != user:
        messages.error(request, "Not Allowed!")
    elif not order.status in REMOVEABLE_ORDER_STATUSES:
        messages.error(request, f"Can't delete order with status {order.status}")
    else:
        order.delete()
        messages.success(request, "Order successfully deleted.")
    return redirect(reverse("orderlist"))


@login_required
def checkout(request):
    user = request.user
    order = get_object_or_404(Order, user=user, status="PENDING")
    subtotal = order.cart_total

    user_address = (
        ShippingAddress.objects.filter(user=user).order_by("date_added").last()
    )
    shipping_form = ShippingAddressForm(instance=user_address)

    if request.method == "POST":
        shipping_form = ShippingAddressForm(request.POST)
        if shipping_form.is_valid():
            data = request.POST
            shipping_address, _ = ShippingAddress.objects.get_or_create(
                address=data.get("address"),
                city=data.get("city"),
                state=data.get("state"),
                zipcode=data.get("zipcode"),
                user=user,
            )
            order.shipping_address = shipping_address
            order.status = "PROCESSING"
            order.save()
            return redirect(reverse("make-payment", kwargs={"order_id": order.id}))

    return render(
        request,
        "products/checkout.html",
        context={
            "form": shipping_form,
            "order": order,
            "subtotal": subtotal,
            "shipping": settings.SHIPPING_PRICE,
            "total": subtotal + settings.SHIPPING_PRICE,
        },
    )


@login_required
def make_payment(request, order_id):
    host = request.get_host()
    order = get_object_or_404(Order, id=order_id)

    paypal_data = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": order.cart_total + settings.SHIPPING_PRICE,
        "item_name": f"ORDER ID: {order.id}",
        "invoice": uuid.uuid4(),
        "currency_code": "USD",
        "notify_url": f"http://{host}{reverse('paypal-ipn')}",
        "return": f"http://{host}{reverse('payment-success', kwargs = {'order_id': order_id})}",
        "cancel_return": f"http://{host}{reverse('payment-failed', kwargs = {'order_id': order_id})}",
    }

    paypal_form = PayPalPaymentsForm(initial=paypal_data)
    context = {
        "shipping": settings.SHIPPING_PRICE,
        "subtotal": order.cart_total,
        "total": order.cart_total + settings.SHIPPING_PRICE,
        "order": order,
        "form": paypal_form,
    }
    return render(request, "products/payment.html", context=context)


def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    update_product_quantity(order)
    order.status = "CONFIRMED"
    order.save()

    return render(request, "products/payment-sucess.html", {"order": order})


def payment_failed(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return render(request, "products/payment-failed.html", {"order": order})
