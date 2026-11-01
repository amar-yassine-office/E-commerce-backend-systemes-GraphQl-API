from django.core.cache import cache
from .models import ShippingZone, ShippingCarrier, ShippingMethod


class ShippingCacheService:
    """إدارة التخزين المؤقت لبيانات الشحن وشركات التوصيل عبر Redis."""

    CACHE_TTL = 60 * 30  # صلاحية الكاش لمدة 30 دقيقة
    ACTIVE_ZONES_KEY = "shipping:active_zones"
    ACTIVE_CARRIERS_KEY = "shipping:active_carriers"
    ACTIVE_METHODS_KEY = "shipping:active_methods"

    @classmethod
    def get_cached_active_zones(cls):
        """جلب مناطق الشحن النشطة من Redis أو تخزينها."""
        zones = cache.get(cls.ACTIVE_ZONES_KEY)
        if zones is None:
            zones = list(ShippingZone.objects.filter(is_active=True))
            cache.set(cls.ACTIVE_ZONES_KEY, zones, cls.CACHE_TTL)
        return zones

    @classmethod
    def get_cached_active_carriers(cls):
        """جلب شركات الشحن النشطة من Redis أو تخزينها."""
        carriers = cache.get(cls.ACTIVE_CARRIERS_KEY)
        if carriers is None:
            carriers = list(ShippingCarrier.objects.filter(is_active=True))
            cache.set(cls.ACTIVE_CARRIERS_KEY, carriers, cls.CACHE_TTL)
        return carriers

    @classmethod
    def get_cached_active_methods(cls):
        """جلب طرق الشحن المتاحة للعملاء مع بيانات شركات الشحن المرتبطة بها."""
        methods = cache.get(cls.ACTIVE_METHODS_KEY)
        if methods is None:
            methods = list(
                ShippingMethod.objects.filter(is_active=True, carrier__is_active=True).select_related('carrier'))
            cache.set(cls.ACTIVE_METHODS_KEY, methods, cls.CACHE_TTL)
        return methods

    @classmethod
    def clear_shipping_cache(cls):
        """مسح كاش الشحن بالكامل عند أي تعديل من لوحة التحكم."""
        cache.delete_many([
            cls.ACTIVE_ZONES_KEY,
            cls.ACTIVE_CARRIERS_KEY,
            cls.ACTIVE_METHODS_KEY,
        ])