from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Warehouse
from .cache import InventoryCacheService


@receiver([post_save, post_delete], sender=Warehouse)
def clear_cache_on_warehouse_change(sender, **kwargs):
    """مسح الكاش تلقائياً عند تغيير أو تحديث بيانات المستودعات."""
    InventoryCacheService.clear_inventory_cache()