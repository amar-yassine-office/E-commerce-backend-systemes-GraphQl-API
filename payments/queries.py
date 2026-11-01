import strawberry
import strawberry_django
from typing import List
from .types import (
    CryptoCurrencyType,
    CryptoTransactionType,
    PaymentWebhookLogType,
    CryptoPayoutType,
)
from .models import (
    CryptoTransaction,
    PaymentWebhookLog,
    CryptoPayout,
)
from .cache import PaymentCacheService


@strawberry.type
class PaymentQuery:
    # جلب العملات المشفرة النشطة باستخدام كاش Redis
    @strawberry.field
    def active_crypto_currencies(self) -> List[CryptoCurrencyType]:
        return PaymentCacheService.get_cached_active_cryptos()

    # استعلامات مباشرة مع دعم الفلترة عبر strawberry_django
    crypto_transactions: List[CryptoTransactionType] = strawberry_django.field()
    payment_webhook_logs: List[PaymentWebhookLogType] = strawberry_django.field()
    crypto_payouts: List[CryptoPayoutType] = strawberry_django.field()