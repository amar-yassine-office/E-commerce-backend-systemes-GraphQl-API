from django.core.cache import cache
from .models import CryptoCurrency


class PaymentCacheService:
    """إدارة التخزين المؤقت (Caching) لبيانات العملات المشفرة المدعومة عبر Redis."""

    CACHE_TTL = 60 * 30  # صلاحية الكاش لمدة 30 دقيقة
    ACTIVE_CRYPTOS_KEY = "payments:active_crypto_currencies"

    @classmethod
    def get_cached_active_cryptos(cls):
        """جلب العملات المشفرة النشطة من Redis أو تخزينها إذا لم تكن موجودة."""
        cryptos = cache.get(cls.ACTIVE_CRYPTOS_KEY)
        if cryptos is None:
            cryptos = list(CryptoCurrency.objects.filter(is_active=True))
            cache.set(cls.ACTIVE_CRYPTOS_KEY, cryptos, cls.CACHE_TTL)
        return cryptos

    @classmethod
    def clear_crypto_cache(cls):
        """مسح الكاش فوراً عند قيام المسؤول بتعديل أو إضافة عملة جديدة في لوحة التحكم."""
        cache.delete(cls.ACTIVE_CRYPTOS_KEY)