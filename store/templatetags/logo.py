from django import template
from store.models import WebsiteInformation

register = template.Library()

@register.filter
def logo(request):
    return WebsiteInformation.objects.filter().order_by('-id')[:1]