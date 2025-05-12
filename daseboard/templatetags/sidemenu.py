from django import template
from store.models import *

register =template.Library()


@register.filter
def category(request):
    return ProductCategory.objects.all()