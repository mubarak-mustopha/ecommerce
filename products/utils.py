from .models import Product, ProductSize


def get_user_or_guest_id(request):
    user = request.user
    if user.is_authenticated:
        return user, ""
    session_key = request.session.session_key
    if not session_key:
        request.session.save()
    return None, request.session.session_key


def update_product_quantity(order):
    products = []
    productsizes = []
    for prod_id, quantity, size in order.orderitems.values_list(
        "product", "quantity", "size"
    ):
        product = Product.objects.get(id=prod_id)
        updated = product.update_quantity(by=-quantity, size=size, commit=False)
        if size:
            productsizes.append(updated)
        else:
            products.append(updated)
    Product.objects.bulk_update(products, fields=["in_stock"])
    ProductSize.objects.bulk_update(productsizes, fields=["quantity"])
