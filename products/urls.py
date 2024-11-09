from django.urls import path

from .views import (
    shop,
    toggle_wishlist,
    wishlist_page,
    cart_update,
    cart_view,
    checkout,
)

urlpatterns = [
    path("", shop, name="shop"),
    path("cart/", cart_view, name="cart"),
    path("cart_update/<uuid:pk>/", cart_update, name="cart_update"),
    path("checkout/", checkout, name="checkout"),
    path("toggle_wishlist/<uuid:pk>/", toggle_wishlist, name="toggle_wishlist"),
    path("wishlist/", wishlist_page, name="wishlist"),
]
