from django import template
from store.models import Order, ReturnProduct
from django.db.models import Subquery

register = template.Library()

@register.filter
def return_items_list(request):
    return_product_items = ReturnProduct.objects.filter(customer=request.user).values('items__id')
    orders = Order.objects.filter(
        user=request.user,
        ordered=True,
        order_status='Complete'
    ).exclude(items__id__in=Subquery(return_product_items))

    order_items = []
    for order in orders:
        remaining_return_days = order.calculate_return_duration()
        order.remaining_return_days = remaining_return_days
        if remaining_return_days > 1:
            order_items.append(order)

    return order_items