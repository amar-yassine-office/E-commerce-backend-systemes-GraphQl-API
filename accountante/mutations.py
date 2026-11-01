import strawberry
from decimal import Decimal
from .types import VendorPayoutType, JournalEntryType
from .models import VendorPayout, JournalEntry
from orders.models import Order


@strawberry.input
class ProcessVendorPayoutInput:
    payout_id: strawberry.ID


@strawberry.type
class AccountanteMutation:
    @strawberry.mutation
    def process_vendor_payout(self, input: ProcessVendorPayoutInput) -> VendorPayoutType:
        """تنفيذ دفع مستحقات التاجر وإنشاء القيد المحاسبي المرتبط بها."""
        try:
            payout = VendorPayout.objects.get(id=input.payout_id)
            AccountingService.execute_vendor_payout(payout)
            return payout
        except VendorPayout.DoesNotExist:
            raise Exception("Vendor payout record not found.")