from django import template
from store.models import WhishLIst

register = template.Library()

@register.filter
def wish_list_product_count(user):
    if user.is_authenticated:
       return WhishLIst.objects.filter(user=user).count()
    return 0