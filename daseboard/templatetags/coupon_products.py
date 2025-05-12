from django import template
from store.models import Coupon
from django.db.models import F
from django.utils import timezone

register = template.Library()

@register.filter
def coupon_products(request):
    now = timezone.now()
    coupon_ids = (
        Coupon.objects.filter(
            is_verified=True,
            valid_to__gte=now,
            used__lt=F('max_value'),
        )
        .values_list('id', flat=True)
        .distinct()
    )
    return list(Coupon.objects.filter(id__in=coupon_ids).prefetch_related('product'))

@register.filter
def coupon_users(request):
    now = timezone.now()
    coupon_ids = (
        Coupon.objects.filter(
            is_verified=True,
            valid_to__gte=now,
            used__lt=F('max_value'),
        )
        .values_list('id', flat=True)
        .distinct()
    )
    return list(Coupon.objects.filter(id__in=coupon_ids).prefetch_related('coupon_user'))

