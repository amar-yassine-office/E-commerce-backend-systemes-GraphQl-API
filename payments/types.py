import strawberry
import strawberry_django
from decimal import Decimal
from .models import (
    CryptoCurrency,
    CryptoTransaction,
    PaymentWebhookLog,
    CryptoPayout,
)

@strawberry_django.type(CryptoCurrency)
class CryptoCurrencyType:
    id: strawberry.ID
    currency_code: str
    name: str
    is_active: bool
    min_amount: Decimal
    max_amount: Decimal | None


@strawberry_django.type(CryptoTransaction)
class CryptoTransactionType:
    id: strawberry.ID
    payment_id: str
    invoice_id: str | None
    price_amount: Decimal
    price_currency: str
    pay_currency: str
    pay_amount: Decimal
    pay_address: str
    actually_paid: Decimal
    outcome_amount: Decimal | None
    status: str
    created_at: str
    updated_at: str


@strawberry_django.type(PaymentWebhookLog)
class PaymentWebhookLogType:
    id: strawberry.ID
    payment_id: str
    event_type: str | None
    is_verified: bool
    received_at: str


@strawberry_django.type(CryptoPayout)
class CryptoPayoutType:
    id: strawberry.ID
    payout_id: str
    address: str
    currency: str
    amount: Decimal
    status: str
    created_at: str