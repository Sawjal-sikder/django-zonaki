from django import template 
from store.models import ProductCategory

register = template.Library()

@register.filter
def category(user):
    cate = ProductCategory.objects.filter(parent=None)   
    return cate