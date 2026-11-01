import strawberry
import strawberry_django
from decimal import Decimal
from .models import (
    Currency,
    ChartOfAccount,
    JournalEntry,
    JournalItem,
    CryptoTransaction,
    TaxRecord,
    VendorPayout,
)

@strawberry_django.type(Currency)
class CurrencyType:
    id: strawberry.ID
    code: str
    symbol: str
    name: str
    exchange_rate_to_base: Decimal
    is_active: bool


@strawberry_django.type(ChartOfAccount)
class ChartOfAccountType:
    id: strawberry.ID
    code: str
    name: str
    account_type: str
    sub_type: str
    currency: CurrencyType
    is_active: bool
    description: str | None


@strawberry_django.type(JournalItem)
class JournalItemType:
    id: strawberry.ID
    debit: Decimal
    credit: Decimal
    memo: str | None
    account: ChartOfAccountType


@strawberry_django.type(JournalEntry)
class JournalEntryType:
    id: strawberry.ID
    entry_number: str
    date: str
    description: str
    source_module: str
    is_posted: bool
    currency: CurrencyType
    items: list[JournalItemType]


@strawberry_django.type(CryptoTransaction)
class CryptoTransactionType:
    id: strawberry.ID
    nowpayments_id: str
    payment_status: str
    pay_address: str
    price_amount: Decimal
    price_currency: str
    pay_amount: Decimal
    pay_currency: str
    actually_paid: Decimal
    created_at: str


@strawberry_django.type(VendorPayout)
class VendorPayoutType:
    id: strawberry.ID
    gross_amount: Decimal
    platform_commission: Decimal
    net_payout_amount: Decimal
    status: str
    payout_method: str
    reference_id: str | None
    processed_at: str | None
    currency: CurrencyType