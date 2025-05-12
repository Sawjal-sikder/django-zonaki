from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from .models import ProductCategory

@receiver([post_save, post_delete], sender=ProductCategory)
def clear_product_category_cache(instance, **kwargs):
    cache.delete('product_category')

