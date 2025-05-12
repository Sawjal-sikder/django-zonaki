from django import template
from store.models import Brand,PriceRange

register = template.Library()

@register.filter
def brands(request):
    return Brand.objects.filter()

@register.filter
def price_ranges(request):
    return PriceRange.objects.filter()