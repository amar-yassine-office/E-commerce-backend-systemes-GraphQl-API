from django.core.cache import cache
from django.utils import timezone
from .models import Coupon, Promotion


class MarketingCacheService:
    """إدارة التخزين المؤقت لبيانات الكوبونات والحملات الترويجية عبر Redis."""

    CACHE_TTL = 60 * 15  # صلاحية الكاش لمدة 15 دقيقة نظراً لارتباطه بتغيرات الأسعار والعروض
    ACTIVE_COUPONS_KEY = "marketing:active_coupons"
    ACTIVE_PROMOTIONS_KEY = "marketing:active_promotions"

    @classmethod
    def get_cached_active_coupons(cls):
        """جلب الكوبونات النشطة والتي ضمن فترة الصلاحية من Redis أو تخزينها مؤقتاً."""
        coupons = cache.get(cls.ACTIVE_COUPONS_KEY)
        if coupons is None:
            now = timezone.now()
            coupons = list(
                Coupon.objects.filter(is_active=True, start_date__lte=now, end_date__gte=now)
            )
            cache.set(cls.ACTIVE_COUPONS_KEY, coupons, cls.CACHE_TTL)
        return coupons

    @classmethod
    def get_cached_active_promotions(cls):
        """جلب الحملات الترويجية النشطة والتي ضمن فترة الصلاحية من Redis أو تخزينها مؤقتاً."""
        promotions = cache.get(cls.ACTIVE_PROMOTIONS_KEY)
        if promotions is None:
            now = timezone.now()
            promotions = list(
                Promotion.objects.filter(is_active=True, start_date__lte=now, end_date__gte=now)
                .prefetch_related('customer_groups', 'categories', 'product_variants')
            )
            cache.set(cls.ACTIVE_PROMOTIONS_KEY, promotions, cls.CACHE_TTL)
        return promotions

    @classmethod
    def clear_marketing_cache(cls):
        """مسح كاش التسويق فوراً عند حدوث أي تعديل على الكوبونات أو الحملات من لوحة التحكم."""
        cache.delete_many([
            cls.ACTIVE_COUPONS_KEY,
            cls.ACTIVE_PROMOTIONS_KEY,
        ])