from django import template
from userapp.models import *

register =template.Library()


@register.filter
def user_profile(request):
    return Profile.objects.filter(user=request.user)