import strawberry
from decimal import Decimal
from .types import VendorPayoutType, JournalEntryType
from .models import VendorPayout, Order
from .services import AccountingService


@strawberry.input
class ProcessVendorPayoutInput:
    payout_id: strawberry.ID


@strawberry.input
class CreateOrderJournalInput:
    order_id: strawberry.ID
    payment_method: str = "crypto"


@strawberry.type
class AccountingMutation:

    @strawberry.mutation
    def process_vendor_payout(self, info, input: ProcessVendorPayoutInput) -> VendorPayoutType:
        """
        استدعاء AccountingService لتنفيذ دفع مستحقات التاجر وتسجيل القيد المحاسبي.
        """
        try:
            payout = VendorPayout.objects.get(id=input.payout_id)
            # استدعاء الدالة من services.py
            AccountingService.execute_vendor_payout(payout)
            return payout
        except VendorPayout.DoesNotExist:
            raise Exception("Vendor payout record not found.")

    @strawberry.mutation
    def create_order_accounting_entry(self, info, input: CreateOrderJournalInput) -> JournalEntryType:
        """
        استدعاء AccountingService لإنشاء القيد المزدوج للطلب عند إتمامه.
        """
        try:
            order = Order.objects.get(id=input.order_id)
            # استدعاء الدالة من services.py مع تحديد طريقة الدفع (كريبتو أو غيره)
            journal_entry = AccountingService.create_order_journal_entry(
                order, payment_method=input.payment_method
            )
            return journal_entry
        except Order.DoesNotExist:
            raise Exception("Order not found.")