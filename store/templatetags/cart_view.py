from django import template
from store.models import Order

register = template.Library()

@register.filter
def cart_view(user):
    if user.is_authenticated:
        cart =Order.objects.filter(user=user, ordered=False)
        return cart


