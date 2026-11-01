import strawberry
from decimal import Decimal
from strawberry.types import Info  # استيراد Info من strawberry
from .types import CryptoPayoutType
from .services import CryptoPaymentService


@strawberry.input
class RequestPayoutInput:
    crypto_tx_id: strawberry.ID
    address: str
    currency: str
    amount: Decimal


@strawberry.type
class PaymentMutation:
    @strawberry.mutation
    def trigger_crypto_transaction_check(self) -> str:
        """تشغيل مهمة فحص المعاملات المعلقة في الخلفية عبر Celery."""
        return CryptoPaymentService.initiate_transaction_check()

    @strawberry.mutation
    def request_crypto_payout(self, info: Info, input: RequestPayoutInput) -> CryptoPayoutType:
        """إنشاء طلب صرف/استرداد جديد وتشغيل مهمة المعالجة."""
        # ملاحظة: تم إضافة ": Info" بجانب info لتجنب الخطأ
        payout = CryptoPaymentService.request_payout(
            crypto_tx_id=input.crypto_tx_id,
            address=input.address,
            currency=input.currency,
            amount=input.amount,
        )
        return payout



