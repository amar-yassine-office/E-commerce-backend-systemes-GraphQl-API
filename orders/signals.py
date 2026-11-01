from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order
from .cache import OrderCacheService


@receiver([post_save, post_delete], sender=Order)
def clear_cache_on_order_change(sender, **kwargs):
    """مسح الكاش تلقائياً عند تغيير حالات أو إنشاء الطلبات."""
    OrderCacheService.clear_order_cache()