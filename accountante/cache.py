from django.core.cache import cache
from .models import ChartOfAccount, Currency


class AccountingCacheService:
    """إدارة التخزين المؤقت (Caching) للبيانات المحاسبية والمالية الثابتة عبر Redis."""

    CACHE_TTL = 60 * 15  # صلاحية الكاش لمدة 15 دقيقة
    COA_CACHE_KEY = "accounting:chart_of_accounts"
    CURRENCY_CACHE_KEY = "accounting:active_currencies"

    @classmethod
    def get_cached_chart_of_accounts(cls):
        """جلب دليل الحسابات من Redis أو تخزينه إذا لم يكن موجوداً."""
        accounts = cache.get(cls.COA_CACHE_KEY)
        if accounts is None:
            accounts = list(ChartOfAccount.objects.filter(is_active=True))
            cache.set(cls.COA_CACHE_KEY, accounts, cls.CACHE_TTL)
        return accounts

    @classmethod
    def get_cached_currencies(cls):
        """جلب العملات النشطة من Redis أو تخزينها."""
        currencies = cache.get(cls.CURRENCY_CACHE_KEY)
        if currencies is None:
            currencies = list(Currency.objects.filter(is_active=True))
            cache.set(cls.CURRENCY_CACHE_KEY, currencies, cls.CACHE_TTL)
        return currencies

    @classmethod
    def clear_accounting_cache(cls):
        """مسح الكاش فوراً عند حدوث أي تعديل على الحسابات أو العملات لتجنب قراءة بيانات قديمة."""
        cache.delete(cls.COA_CACHE_KEY)
        cache.delete(cls.CURRENCY_CACHE_KEY)