from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import CryptoTransaction, CryptoPayout

# استيراد المهام من تطبيق payments
from .tasks import check_pending_crypto_transactions, process_crypto_payout_task


class CryptoPaymentService:
    """خدمة إدارة المدفوعات والعمليات المشفرة في تطبيق payments."""

    @staticmethod
    @transaction.atomic
    def initiate_transaction_check():
        """
        تشغيل مهمة التحقق من المعاملات في الخلفية عبر Celery.
        """
        check_pending_crypto_transactions.delay()
        return "Background task for checking pending crypto transactions has been triggered."

    @staticmethod
    @transaction.atomic
    def request_payout(crypto_tx_id, address, currency, amount):
        """
        إنشاء طلب صرف/استرداد جديد وتشغيل مهمة المعالجة عبر Celery.
        """
        crypto_tx = CryptoTransaction.objects.filter(id=crypto_tx_id).first()

        payout = CryptoPayout.objects.create(
            payout_id=f"payout-{timezone.now().timestamp()}",
            crypto_transaction=crypto_tx,
            address=address,
            currency=currency,
            amount=amount,
            status=CryptoPayout.Status.CREATED,
        )

        # تشغيل مهمة معالجة الصرف في الخلفية
        process_crypto_payout_task.delay(payout.id)
        return payout