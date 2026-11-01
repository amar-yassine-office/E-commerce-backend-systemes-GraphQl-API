from django.core.cache import cache
from .models import Warehouse


class InventoryCacheService:
    """إدارة التخزين المؤقت لبيانات المستودعات والبنية التحتية للمخزون عبر Redis."""

    CACHE_TTL = 60 * 30  # صلاحية الكاش لمدة 30 دقيقة
    ACTIVE_WAREHOUSES_KEY = "inventory:active_warehouses"

    @classmethod
    def get_cached_active_warehouses(cls):
        """جلب المستودعات النشطة من Redis أو تخزينها مؤقتاً."""
        warehouses = cache.get(cls.ACTIVE_WAREHOUSES_KEY)
        if warehouses is None:
            warehouses = list(Warehouse.objects.filter(is_active=True))
            cache.set(cls.ACTIVE_WAREHOUSES_KEY, warehouses, cls.CACHE_TTL)
        return warehouses

    @classmethod
    def clear_inventory_cache(cls):
        """مسح كاش المستودعات فوراً عند حدوث أي تعديل من لوحة التحكم."""
        cache.delete(cls.ACTIVE_WAREHOUSES_KEY)