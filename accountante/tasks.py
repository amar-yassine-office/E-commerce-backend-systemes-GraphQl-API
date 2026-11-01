from celery import shared_task
from django.utils import timezone
from .models import CryptoTransaction, VendorPayout
from .services import AccountingService


@shared_task(bind=True, max_retries=3)
def check_pending_crypto_transactions(self):
    """
    مهام خلفية للتحقق من معاملات NOWPayments المعلقة وتحديث حالتها.
    يمكن جدولتها للعمل كل بضع دقائق عبر Celery Beat.
    """
    pending_txs = CryptoTransaction.filter(
        payment_status__in=[
            CryptoTransaction.PaymentStatus.WAITING,
            CryptoTransaction.PaymentStatus.CONFIRMING,
        ]
    )

    updated_count = 0
    for tx in pending_txs:
        try:
            # استدعاء خدمة التحقق من بوابة NOWPayments (افتراضي)
            is_updated = AccountingService.verify_nowpayments_status(tx)
            if is_updated:
                updated_count += 1
        except Exception as exc:
            # إعادة المحاولة في حال فشل الاتصال بالبوابة
            raise self.retry(exc=exc, countdown=60)

    return f"Successfully checked {pending_txs.count()} transactions. Updated: {updated_count}"


@shared_task
def process_vendor_payout_task(payout_id):
    """
    معالجة دفعات التجار (Vendor Payouts) في الخلفية وتحويل القيود المحاسبية.
    """
    try:
        payout = VendorPayout.objects.get(id=payout_id, status=VendorPayout.PayoutStatus.PENDING)
        AccountingService.execute_vendor_payout(payout)
        return f"Vendor Payout {payout_id} processed successfully."
    except VendorPayout.DoesNotExist:
        return f"Vendor Payout {payout_id} not found or already processed."