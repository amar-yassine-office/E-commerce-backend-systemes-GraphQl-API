# payments/services.py
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import CryptoTransaction, CryptoPayout, CryptoCurrency
from .cache import PaymentCacheService
from .tasks import check_pending_crypto_transactions, process_crypto_payout_task


class CryptoPaymentService:
    """خدمة إدارة مدفوعات NOWPayments والعمليات المشفرة في تطبيق payments."""

    @staticmethod
    @transaction.atomic
    def initiate_transaction_check():
        """
        تشغيل مهمة Celery للتحقق من معاملات الكريبتو المعلقة في الخلفية.
        """
        check_pending_crypto_transactions.delay()
        return "Background task for checking pending crypto transactions has been triggered."

    @staticmethod
    @transaction.atomic
    def create_crypto_transaction(order, pay_currency: str, price_amount: Decimal, price_currency: str = "USD"):
        """
        إنشاء معاملة دفع كريبتو جديدة مرتبطة بالطلب مع التحقق من تفعيل العملة عبر الكاش.
        """
        # التحقق أن العملة مدعومة ومفعلة باستخدام كاش Redis
        active_cryptos = PaymentCacheService.get_cached_active_cryptos()
        is_supported = any(c.currency_code.lower() == pay_currency.lower() for c in active_cryptos)

        if not is_supported:
            raise ValueError(f"Cryptocurrency '{pay_currency}' is not supported or currently inactive.")

        # إنشاء سجل المعاملة الجديد
        crypto_tx = CryptoTransaction.objects.create(
            order=order,
            payment_id=f"np-pay-{timezone.now().timestamp()}",
            price_amount=price_amount,
            price_currency=price_currency,
            pay_currency=pay_currency.lower(),
            pay_amount=price_amount,  # (سيتم جلب القيمة الحقيقية تلقائياً من استجابة NOWPayments API)
            pay_address="placeholder_wallet_address",  # (عنوان المحفظة الوارد من بوابة الدفع)
            status=CryptoTransaction.Status.WAITING,
        )
        return crypto_tx

    @staticmethod
    @transaction.atomic
    def request_payout(crypto_tx_id, address, currency, amount):
        """
        إنشاء طلب صرف/استرداد جديد للمستحقات وتشغيل مهمة المعالجة عبر Celery.
        """
        crypto_tx = CryptoTransaction.objects.filter(id=crypto_tx_id).first()

        payout = CryptoPayout.objects.create(
            payout_id=f"payout-{timezone.now().timestamp()}",
            crypto_transaction=crypto_tx,
            address=address,
            currency=currency.lower(),
            amount=amount,
            status=CryptoPayout.Status.CREATED,
        )

        # تشغيل مهمة معالجة الصرف في الخلفية لعدم إبطاء استجابة السيرفر
        process_crypto_payout_task.delay(payout.id)
        return payout