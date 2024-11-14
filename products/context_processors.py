from .models import OrderItem, Order
from .utils import get_user_or_guest_id


def cartitems_count(request):
    user, guest_id = get_user_or_guest_id(request)
    order = (
        Order.objects.filter(user=user, guest_id=guest_id, status="PENDING").first()
        or []
    )

    return {"cartitems_count": len(order)}
