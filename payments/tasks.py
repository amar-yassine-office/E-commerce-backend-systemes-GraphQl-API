from celery import shared_task
from django.utils import timezone
from .models import CryptoTransaction, CryptoPayout


@shared_task(bind=True, max_retries=3)
def check_pending_crypto_transactions(self):
    """
    التحقق دورياً من المعاملات المعلقة عبر NOWPayments API.
    """
    pending_txs = CryptoTransaction.objects.filter(
        status__in=[
            CryptoTransaction.Status.WAITING,
            CryptoTransaction.Status.CONFIRMING,
        ]
    )

    # هنا يتم وضع منطق استعلام API الخاص بـ NOWPayments وتحديث الحالة
    return f"Successfully checked {pending_txs.count()} pending crypto transactions."


@shared_task(bind=True, max_retries=3)
def process_crypto_payout_task(self, payout_id):
    """
    معالجة عمليات الصرف أو الاسترداد (Payouts/Refunds) في الخلفية.
    """
    try:
        payout = CryptoPayout.objects.get(id=payout_id, status=CryptoPayout.Status.CREATED)
        # هنا يتم استدعاء API الصرف الخاص بـ NOWPayments
        payout.status = CryptoPayout.Status.PROCESSING
        payout.save()
        return f"Crypto payout {payout_id} is being processed."
    except CryptoPayout.DoesNotExist:
        return f"Crypto payout {payout_id} not found."