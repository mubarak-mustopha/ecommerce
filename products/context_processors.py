from .models import OrderItem
from .utils import get_user_or_guest_id


def cartitems_count(request):
    user, guest_id = get_user_or_guest_id(request)
    orderitems = OrderItem.objects.filter(user=user, guest_id=guest_id, order=None)
    return {"cartitems_count": sum([orderitem.quantity for orderitem in orderitems])}
