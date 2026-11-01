from django.core.cache import cache
from .models import Order


class OrderCacheService:
    """إدارة التخزين المؤقت لإحصائيات الطلبات لوحة التحكم عبر Redis."""

    CACHE_TTL = 60 * 5  # صلاحية قصيرة (5 دقائق) نظراً لتغير حالة الطلبات باستمرار
    PENDING_ORDERS_COUNT_KEY = "orders:pending_count"

    @classmethod
    def get_cached_pending_orders_count(cls):
        """جلب عدد الطلبات المعلقة من الكاش أو حسابها وتخزينها."""
        count = cache.get(cls.PENDING_ORDERS_COUNT_KEY)
        if count is None:
            count = Order.objects.filter(status=Order.Status.PENDING).count()
            cache.set(cls.PENDING_ORDERS_COUNT_KEY, count, cls.CACHE_TTL)
        return count

    @classmethod
    def clear_order_cache(cls):
        """مسح كاش إحصائيات الطلبات فور إنشاء طلب جديد أو تعديل حالته."""
        cache.delete(cls.PENDING_ORDERS_COUNT_KEY)