from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Category, Brand
from .cache import CatalogCacheService


@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=Brand)
def clear_cache_on_catalog_change(sender, **kwargs):
    """مسح الكاش تلقائياً عند تغيير التصنيفات أو العلامات التجارية."""
    CatalogCacheService.clear_catalog_cache()