from django.db.models import Count
from django.core.paginator import Paginator
from django.shortcuts import render

from .models import Product, Category


# Create your views here.
def shop(request):
    top_cats = Category.objects.annotate(Count("products")).order_by("-products__count")
    products = Product.objects.prefetch_related("productsizes")

    paginator = Paginator(products, 2)
    page_num = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_num)
    page_range = paginator.page_range

    context = {
        "categories": Category.objects.values_list("name", flat=True),
        "page_obj": page_obj,
        "page_range": page_range,
        "current_page": int(page_num),
    }

    from pprint import pprint

    pprint(context)
    return render(request, "products/shop.html", context)

