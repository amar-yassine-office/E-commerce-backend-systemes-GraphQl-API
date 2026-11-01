import strawberry
import strawberry_django
from typing import List
from .types import (
    ChartOfAccountType,
    JournalEntryType,
    CryptoTransactionType,
    VendorPayoutType,
    CurrencyType,
)
from .models import (
    ChartOfAccount,
    JournalEntry,
    CryptoTransaction,
    VendorPayout,
    Currency,
)
from .cache import AccountingCacheService


@strawberry.type
class AccountanteQuery:
    # استخدام كاش Redis لدليل الحسابات والعملات لتحسين السرعة
    @strawberry.field
    def active_chart_of_accounts(self) -> List[ChartOfAccountType]:
        return AccountingCacheService.get_cached_chart_of_accounts()

    @strawberry.field
    def active_currencies(self) -> List[CurrencyType]:
        return AccountingCacheService.get_cached_currencies()

    # استعلامات مباشرة من قاعدة البيانات مع فلترة
    journal_entries: List[JournalEntryType] = strawberry_django.field()
    crypto_transactions: List[CryptoTransactionType] = strawberry_django.field()
    vendor_payouts: List[VendorPayoutType] = strawberry_django.field()