from django import template
from store.models import Order

register = template.Library()

@register.filter
def commission_earning_filter(request):
    total_commission = 0
    try:
        # Get all completed orders and prefetch related items
        orders = Order.objects.filter(ordered=True).prefetch_related('items__item')
        for order in orders:
            # Loop through the related items for each order
            for order_item in order.items.all():
                if not order_item.pathao_consignment_id or order_item.pathao_status != "Delivered":
                    continue
                commission = order_item.item.calculate_commission()
                if commission is not None:
                    total_commission += commission
    
    except Exception as e:
        pass
    return total_commission
