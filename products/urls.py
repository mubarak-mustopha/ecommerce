from django.urls import path

from .views import *

urlpatterns = [
    path("", shop, name="shop"),
    path("cart/", cart_view, name="cart"),
    path("cart_update/<uuid:pk>/", cart_update, name="cart_update"),
    path("checkout/", checkout, name="checkout"),
    path("payment/success/<uuid:order_id>/", payment_success, name="payment-success"),
    path("payment/failed/<uuid:order_id>/", payment_failed, name="payment-failed"),
    path("payment/make_payment/<uuid:order_id>/", make_payment, name="make-payment"),
    path("orderlist/", orderlist_view, name="orderlist"),
    path("order_delete/<uuid:order_id>/", order_delete_view, name="order-delete"),
    path("toggle_wishlist/<uuid:pk>/", toggle_wishlist, name="toggle_wishlist"),
    path("wishlist/", wishlist_page, name="wishlist"),
]
