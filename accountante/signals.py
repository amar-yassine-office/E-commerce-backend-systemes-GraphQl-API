from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ChartOfAccount, Currency
from .cache import AccountingCacheService

@receiver([post_save, post_delete], sender=ChartOfAccount)
@receiver([post_save, post_delete], sender=Currency)
def clear_cache_on_accounting_change(sender, **kwargs):
    AccountingCacheService.clear_accounting_cache()