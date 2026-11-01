from django.core.cache import cache
from .models import Category, Brand


class CatalogCacheService:
    """إدارة التخزين المؤقت لبيانات الكتالوج (التصنيفات والعلامات التجارية) عبر Redis."""

    CACHE_TTL = 60 * 30  # صلاحية الكاش لمدة 30 دقيقة
    ACTIVE_CATEGORIES_KEY = "catalog:active_categories"
    ACTIVE_BRANDS_KEY = "catalog:active_brands"

    @classmethod
    def get_cached_active_categories(cls):
        """جلب التصنيفات النشطة من Redis أو تخزينها مؤقتاً."""
        categories = cache.get(cls.ACTIVE_CATEGORIES_KEY)
        if categories is None:
            categories = list(Category.objects.filter(is_active=True).select_related('parent'))
            cache.set(cls.ACTIVE_CATEGORIES_KEY, categories, cls.CACHE_TTL)
        return categories

    @classmethod
    def get_cached_active_brands(cls):
        """جلب العلامات التجارية النشطة من Redis أو تخزينها مؤقتاً."""
        brands = cache.get(cls.ACTIVE_BRANDS_KEY)
        if brands is None:
            brands = list(Brand.objects.filter(is_active=True))
            cache.set(cls.ACTIVE_BRANDS_KEY, brands, cls.CACHE_TTL)
        return brands

    @classmethod
    def clear_catalog_cache(cls):
        """مسح كاش الكتالوج فوراً عند حدوث أي تعديل من لوحة التحكم."""
        cache.delete_many([
            cls.ACTIVE_CATEGORIES_KEY,
            cls.ACTIVE_BRANDS_KEY,
        ])