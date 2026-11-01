from django.core.cache import cache
from .models import CustomerGroup


class CustomerCacheService:
    """إدارة التخزين المؤقت لبيانات فئات العملاء وسياسات الخصم عبر Redis."""

    CACHE_TTL = 60 * 30  # صلاحية الكاش لمدة 30 دقيقة
    ACTIVE_CUSTOMER_GROUPS_KEY = "customers:active_groups"

    @classmethod
    def get_cached_customer_groups(cls):
        """جلب فئات العملاء من Redis أو تخزينها مؤقتاً."""
        groups = cache.get(cls.ACTIVE_CUSTOMER_GROUPS_KEY)
        if groups is None:
            groups = list(CustomerGroup.objects.all())
            cache.set(cls.ACTIVE_CUSTOMER_GROUPS_KEY, groups, cls.CACHE_TTL)
        return groups

    @classmethod
    def clear_customer_cache(cls):
        """مسح كاش العملاء وفئاتهم فوراً عند حدوث أي تعديل من لوحة التحكم."""
        cache.delete(cls.ACTIVE_CUSTOMER_GROUPS_KEY)