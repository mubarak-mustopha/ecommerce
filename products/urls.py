from django.urls import path

from .views import shop, toggle_wishlist, wishlist_page

urlpatterns = [
    path("", shop, name="shop"),
    path("toggle_wishlist/<uuid:pk>/", toggle_wishlist, name="toggle_wishlist"),
    path("wishlist/", wishlist_page, name="wishlist"),
]
