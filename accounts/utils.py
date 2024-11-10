import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from products.models import WishList, Order, OrderItem


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk)
            + six.text_type(timestamp)
            + six.text_type(user.is_email_verified)
        )


email_token_generator = EmailVerificationTokenGenerator()


def add_guest_data(request, user):
    guest_id = request.session.session_key
    if not guest_id:
        return
    guest_wishlist = WishList.objects.filter(guest_id=guest_id)
    guest_order = Order.objects.filter(guest_id=guest_id).first()

    user_wishlist_products = user.wishlist_set.values_list("product", flat=True)
    user_pending_order = user.orders.filter(status="PENDING").first()

    # update wishlist
    guest_wishlist.filter(product__in=user_wishlist_products).delete()
    guest_wishlist.update(guest_id="", user=user)

    # update order
    if not user_pending_order:
        guest_order.update(guest_id="", user=user)
    else:
        non_duplicate_orderitems = []
        for orderitem in guest_order:
            kwargs = {
                "product": orderitem.product,
                "size": orderitem.size,
                "color": orderitem.color,
            }
            if not user_pending_order.orderitems.filter(**kwargs):
                non_duplicate_orderitems.append(orderitem)
                orderitem.order = user_pending_order
        OrderItem.objects.bulk_update(non_duplicate_orderitems, ["order"])
        guest_order.delete()
