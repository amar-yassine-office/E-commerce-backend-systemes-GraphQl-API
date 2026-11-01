# Create your models here.
from decimal import Decimal

from django.db import models
from orders.models import Order


class CryptoCurrency(models.Model):
    """Catalog of supported cryptocurrencies fetched/synced from NOWPayments API"""
    currency_code = models.CharField(max_length=20, unique=True, verbose_name="رمز العملة (مثل btc, usdttrc20)")
    name = models.CharField(max_length=100, verbose_name="اسم العملة الكامل")
    is_active = models.BooleanField(default=True, verbose_name="متاحة للدفع")
    min_amount = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0.00000000'),
                                     verbose_name="الحد الأدنى للدفعة")
    max_amount = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True,
                                     verbose_name="الحد الأقصى للدفعة")

    class Meta:
        verbose_name = "عملة مشفرة مدعومة"
        verbose_name_plural = "العملات المشفرة المدعومة"

    def __str__(self):
        return f"{self.name} ({self.currency_code.upper()})"


class CryptoTransaction(models.Model):
    """Core payment transaction and invoice tracking linked to NOWPayments"""

    class Status(models.TextChoices):
        WAITING = 'waiting', 'في انتظار التحويل (Waiting)'
        CONFIRMING = 'confirming', 'قيد التأكيد على الشبكة (Confirming)'
        CONFIRMED = 'confirmed', 'تم تأكيد الدفع (Confirmed)'
        SENDING = 'sending', 'قيد التحويل للمحفظة الرئيسية (Sending)'
        PARTIALLY_PAID = 'partially_paid', 'مدفوع جزئياً (Partially Paid)'
        FINISHED = 'finished', 'مكتمل بنجاح (Finished)'
        FAILED = 'failed', 'فشل المعاملة (Failed)'
        EXPIRED = 'expired', 'انتهت مهلة الدفع (Expired)'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='crypto_transactions',
                              verbose_name="الطلب المرتبط")

    # NOWPayments Identifiers
    payment_id = models.CharField(max_length=100, unique=True, verbose_name="معرف العملية في NOWPayments")
    invoice_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="معرف الفاتورة (إن وجدت)")

    # Fiat Pricing (e.g., USD, EUR)
    price_amount = models.DecimalField(max_digits=12, decimal_places=2,
                                       verbose_name="المبلغ الأساسي بالفاتورة التقليدية")
    price_currency = models.CharField(max_length=10, default='USD', verbose_name="عملة الفاتورة التقليدية")

    # Crypto Payment Details
    pay_currency = models.CharField(max_length=20, verbose_name="العملة المشفرة المختارة للدفع")
    pay_amount = models.DecimalField(max_digits=24, decimal_places=8, verbose_name="المبلغ المطلوب بالعملة المشفرة")
    pay_address = models.CharField(max_length=255, verbose_name="عنوان المحفظة المخصص للتحويل")

    # Actual Received Data
    actually_paid = models.DecimalField(max_digits=24, decimal_places=8, default=Decimal('0.00000000'),
                                        verbose_name="المبلغ الفعلي المستلم على الشبكة")
    outcome_amount = models.DecimalField(max_digits=24, decimal_places=8, null=True, blank=True,
                                         verbose_name="صافي المبلغ المحول للمحفظة بعد الرسوم")

    status = models.CharField(max_length=30, choices=Status.choices, default=Status.WAITING,
                              verbose_name="حالة معاملة الكريبتو")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    class Meta:
        verbose_name = "معاملة دفع كريبتو"
        verbose_name_plural = "معاملات دفع الكريبتو"

    def __str__(self):
        return f"Payment #{self.payment_id} | Order #{self.order.id} | {self.pay_currency.upper()} ({self.status})"


class PaymentWebhookLog(models.Model):
    """Secure IPN (Instant Payment Notification) Webhook audit log"""
    payment_id = models.CharField(max_length=100, verbose_name="معرف المعاملة الوارد")
    event_type = models.CharField(max_length=100, blank=True, null=True, verbose_name="نوع الحدث")
    payload = models.JSONField(verbose_name="بيانات الإشعار الكاملة (JSON)")
    is_verified = models.BooleanField(default=False, verbose_name="تم التحقق من HMAC Signature")
    received_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الاستلام")

    class Meta:
        verbose_name = "سجل Webhook الدفع"
        verbose_name_plural = "سجلات Webhooks الدفع"

    def __str__(self):
        return f"IPN Log #{self.id} - Payment: {self.payment_id} (Verified: {self.is_verified})"


class CryptoPayout(models.Model):
    """Enterprise Payouts/Refunds management via NOWPayments Payout API"""

    class Status(models.TextChoices):
        CREATED = 'created', 'تم الإنشاء'
        PROCESSING = 'processing', 'قيد المعالجة'
        FINISHED = 'finished', 'مكتمل'
        FAILED = 'failed', 'فشل الصرف'

    payout_id = models.CharField(max_length=100, unique=True, verbose_name="معرف عملية الصرف")
    crypto_transaction = models.ForeignKey(CryptoTransaction, on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='payouts', verbose_name="معاملة الأصل (للإرجاع)")

    address = models.CharField(max_length=255, verbose_name="عنوان محفظة المستقبل")
    currency = models.CharField(max_length=20, verbose_name="عملة الصرف المشفرة")
    amount = models.DecimalField(max_digits=24, decimal_places=8, verbose_name="المبلغ المراد صرفه")

    status = models.CharField(max_length=30, choices=Status.choices, default=Status.CREATED, verbose_name="حالة الصرف")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")

    class Meta:
        verbose_name = "عملية صرف/استرداد كريبتو"
        verbose_name_plural = "عمليات الصرف والاسترداد"

    def __str__(self):
        return f"Payout #{self.payout_id} - {self.amount} {self.currency.upper()}"