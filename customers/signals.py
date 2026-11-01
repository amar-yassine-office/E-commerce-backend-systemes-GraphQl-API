from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CustomerGroup
from .cache import CustomerCacheService


@receiver([post_save, post_delete], sender=CustomerGroup)
def clear_cache_on_customer_group_change(sender, **kwargs):
    """مسح الكاش تلقائياً عند تغيير فئات العملاء أو نسب الخصم."""
    CustomerCacheService.clear_customer_cache()