from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CryptoCurrency
from .cache import PaymentCacheService

@receiver([post_save, post_delete], sender=CryptoCurrency)
def clear_crypto_cache_on_change(sender, **kwargs):
    PaymentCacheService.clear_crypto_cache()