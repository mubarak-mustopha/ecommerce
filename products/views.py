from django.db.models import Count, Case, Value, When
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render

from .models import Product, Category, WishList


# Create your views here.
def shop(request):
    top_cats = Category.objects.annotate(Count("products")).order_by("-products__count")
    products = Product.objects.prefetch_related("productsizes")

    paginator = Paginator(products, 2)
    page_num = request.GET.get("page", 1)
    products = paginator.get_page(page_num).object_list
    page_range = paginator.page_range

    if request.user.is_authenticated:
        products = products.annotate(
            in_wishlist=Case(
                When(
                    id__in=request.user.wishlist_set.values_list(
                        "product_id", flat=True
                    ),
                    then=Value(True),
                ),
                default=Value(False),
            )
        )

    context = {
        "categories": Category.objects.values_list("name", flat=True),
        "products": products,
        "page_range": page_range,
        "current_page": int(page_num),
    }

    return render(request, "products/shop.html", context)


def toggle_wishlist(request, pk):
    data = {}
    product = Product.objects.filter(id=pk)

    if not product.exists():
        return JsonResponse(data={"error": "Invalid id for product"}, status=400)

    if request.user.is_authenticated:
        wishlist, created = WishList.objects.get_or_create(
            product=product.first(),
            user=request.user,
        )
        if not created:
            wishlist.delete()
        data = {"success": True}
    else:
        wishlist = request.session.get("wishlist")
        if not wishlist:
            wishlist = request.session["wishlist"] = [str(pk)]
        else:
            if str(pk) in wishlist:
                wishlist.remove(str(pk))
            else:
                wishlist.append(str(pk))
        request.session.modified = True
        data = {"success": True}
    return JsonResponse(data)
