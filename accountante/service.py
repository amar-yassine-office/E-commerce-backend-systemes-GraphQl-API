from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import (
    ChartOfAccount,
    CryptoTransaction,
    JournalEntry,
    JournalItem,
    TaxRecord,
    VendorPayout,
)


class AccountingService:
    """خدمة مركزية لإدارة العمليات المحاسبية والمالية للمتجر."""

    @staticmethod
    @transaction.atomic
    def create_order_journal_entry(order, payment_method="crypto"):
        """
        إنشاء قيد محاسبي مزدوج عند إتمام الطلب بنجاح (إيرادات المبيعات + ضريبة القيمة المضافة).
        """
        # جلب الحسابات الافتراضية من الدليل المحاسبي (Chart of Accounts)
        sales_account = ChartOfAccount.objects.get(sub_type="sales_revenue")
        receivable_or_cash = ChartOfAccount.objects.get(
            sub_type="crypto_wallet" if payment_method == "crypto" else "cash")
        tax_payable_account = ChartOfAccount.objects.get(sub_type="tax_payable")

        # إنشاء قيد اليومية
        entry = JournalEntry.objects.create(
            entry_number=f"JE-ORD-{order.id}",
            date=timezone.now().date(),
            description=f"Revenue entry for Order #{order.id}",
            source_module=JournalEntry.SourceModule.ORDER,
            currency=order.currency,
            order=order,
            is_posted=True,
        )

        total_amount = order.total_amount
        tax_amount = getattr(order, "tax_amount", Decimal("0.00"))
        net_sales = total_amount - tax_amount

        # من حساب النقدية / المحفظة (مدين - Debit)
        JournalItem.objects.create(
            journal_entry=entry,
            account=receivable_or_cash,
            debit=total_amount,
            credit=Decimal("0.0000"),
            memo=f"Total collected for Order #{order.id}",
        )

        # إلى حساب إيرادات المبيعات (دائن - Credit)
        JournalItem.objects.create(
            journal_entry=entry,
            account=sales_account,
            debit=Decimal("0.0000"),
            credit=net_sales,
            memo=f"Net sales revenue for Order #{order.id}",
        )

        # إلى حساب ضرائب المبيعات المستحقة إن وجدت (دائن - Credit)
        if tax_amount > 0:
            JournalItem.objects.create(
                journal_entry=entry,
                account=tax_payable_account,
                debit=Decimal("0.0000"),
                credit=tax_amount,
                memo=f"Tax payable for Order #{order.id}",
            )

        return entry

    @staticmethod
    def verify_nowpayments_status(crypto_tx: CryptoTransaction) -> bool:
        """
        منطق الاتصال بـ NOWPayments API للتحقق من حالة الدفع وتحديث القيد إذا اكتمل.
        """
        # ملاحظة: هنا تضع استدعاء API الخاص بـ NOWPayments باستخدام مكتبة `requests`
        # مثال وهمي لتحديث الحالة:
        # response = requests.get(f"https://api.nowpayments.io/v1/payment/{crypto_tx.nowpayments_id}", headers=...)

        # إذا تم التأكد من اكتمال الدفع (finished):
        # crypto_tx.payment_status = CryptoTransaction.PaymentStatus.FINISHED
        # crypto_tx.save()

        # AccountingService.create_order_journal_entry(crypto_tx.order, payment_method="crypto")
        return False

    @staticmethod
    @transaction.atomic
    def execute_vendor_payout(payout: VendorPayout):
        """
        تنفيذ عملية دفع مستحقات التاجر وتسجيل القيد المحاسبي للعمولة والتحويل.
        """
        payout.status = VendorPayout.PayoutStatus.COMPLETED
        payout.processed_at = timezone.now()
        payout.save()

        # إنشاء قيد محاسبي لصرف المستحقات للتاجر وتخفيض التزام المنصة (Vendor Payable)
        payable_account = ChartOfAccount.objects.get(sub_type="vendor_payable")
        cash_account = ChartOfAccount.objects.get(sub_type="cash")

        entry = JournalEntry.objects.create(
            entry_number=f"JE-PAYOUT-{payout.id}",
            date=timezone.now().date(),
            description=f"Payout transfer to vendor {payout.vendor.name}",
            source_module=JournalEntry.SourceModule.VENDOR,
            currency=payout.currency,
            vendor=payout.vendor,
            is_posted=True,
        )

        # تخفيض التزام التاجر (مدين)
        JournalItem.objects.create(
            journal_entry=entry,
            account=payable_account,
            debit=payout.net_payout_amount,
            credit=Decimal("0.0000"),
            memo=f"Clearing vendor payable for Payout #{payout.id}",
        )

        # خروج الأموال من حساب المنصة (دائن)
        JournalItem.objects.create(
            journal_entry=entry,
            account=cash_account,
            debit=Decimal("0.0000"),
            credit=payout.net_payout_amount,
            memo=f"Cash outflow for Payout #{payout.id}",
        )

        payout.journal_entry = entry
        payout.save()

        # the cache

        # لجلب الحسابات المحاسبية مباشرة من الكاش
        active_accounts = AccountingCacheService.get_cached_chart_of_accounts()

        # لجلب العملات النشطة من الكاش
        active_currencies = AccountingCacheService.get_cached_currencies()