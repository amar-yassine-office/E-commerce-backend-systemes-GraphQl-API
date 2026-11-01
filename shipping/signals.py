from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ShippingZone, ShippingCarrier, ShippingMethod, ShippingRate
from .cache import ShippingCacheService


@receiver([post_save, post_delete], sender=ShippingZone)
@receiver([post_save, post_delete], sender=ShippingCarrier)
@receiver([post_save, post_delete], sender=ShippingMethod)
@receiver([post_save, post_delete], sender=ShippingRate)
def clear_cache_on_shipping_change(sender, **kwargs):
    """مسح الكاش فوراً عند حدوث أي تغيير في إعدادات أو أسعار الشحن."""
    ShippingCacheService.clear_shipping_cache()