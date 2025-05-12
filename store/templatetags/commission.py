from django import template
from store.models import Order

register = template.Library()

@register.filter
def commission_filter(order_id, user):
    total_commission = 0
    user = int(user)
    try:
        order = Order.objects.get(id=order_id, ordered=True)
        for order_item in order.items.all():
            if order_item.item.user.id == user:
                commission = order_item.item.calculate_commission()
                if commission is not None:
                    total_commission += commission
    except Order.DoesNotExist:
        print('Order with id', order_id, 'does not exist.')
    except Exception as e:
        print('An error occurred:', e)
    return total_commission


# @register.filter
# def vendor_total_price_filter(order_id,user):
#     user = int(user)
#     total = 0
#     order = Order.objects.get(id=order_id, ordered=True)
#     for order_item in order.items.all():
#         if order_item.item.user.id == user:
#             total += order_item.vendor_total_price()
#             print('total=======================', total)
#             return total

from decimal import Decimal

# @register.filter
# def vendor_total_price_filter(order_id, user):
#     user = int(user)
#     total = Decimal(0)
#     order = Order.objects.get(id=order_id, ordered=True)
#     vendor_total = Decimal(0)
    
#     if order.coupon:
#         if order.coupon.coupon_type == 'Percentage':
#             discount = (Decimal(order.coupon.amount_or_percentage) / Decimal(100)) * vendor_total
#             vendor_total -= discount
#         elif order.coupon.coupon_type == 'Amount':
#             total_order_price = sum(Decimal(item.get_subtotal()) for item in order.items.all())
#             if total_order_price > 0:
#                 proportional_discount = (vendor_total / total_order_price) * Decimal(order.coupon.amount_or_percentage)
#                 vendor_total -= proportional_discount
#         return max(vendor_total, Decimal(0))
#     else:
#        for order_item in order.items.all():
#         if order_item.item.user.id == user:
#             total += order_item.vendor_total_price()
#             return total

@register.filter
def vendor_total_price_filter(order_id, user):
    user = int(user)
    total = Decimal(0)
    order = Order.objects.get(id=order_id, ordered=True)
    for order_item in order.items.all():
        if order_item.item.user.id == user:
            total += order_item.vendor_total_price()
            return total
    
def remove_order_coupon_amount(order_id, total_vendor_price):
    order = Order.objects.get(id=order_id, ordered=True)
    if order.coupon:
        if order.coupon.coupon_type == 'Percentage':
            discount = (Decimal(order.coupon.amount_or_percentage) / Decimal(100)) * total_vendor_price
            total_vendor_price -= discount
        elif order.coupon.coupon_type == 'Amount':
            total_vendor_price = total_vendor_price - Decimal(order.coupon.amount_or_percentage)
        return total_vendor_price
    return total_vendor_price


@register.filter
def vendor_commission_from_total(order_id, user_id):
    total_vendor_price = vendor_total_price_filter(order_id, user_id)
    total_vendor_price_after_coupon = remove_order_coupon_amount(order_id, total_vendor_price)
    total_commission = commission_filter(order_id, user_id)
    return total_vendor_price_after_coupon - total_commission