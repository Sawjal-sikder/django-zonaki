from django import template
from store.models import Order
register = template.Library()

@register.filter
def cart_count(user):
    if user.is_authenticated:
        qs=Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].items.count()
        return 0
    return 0


