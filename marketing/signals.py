from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Coupon, Promotion
from .cache import MarketingCacheService


@receiver([post_save, post_delete], sender=Coupon)
@receiver([post_save, post_delete], sender=Promotion)
def clear_cache_on_marketing_change(sender, **kwargs):
    """مسح الكاش تلقائياً عند تحديث أو تغيير الكوبونات والحملات الترويجية."""
    MarketingCacheService.clear_marketing_cache()