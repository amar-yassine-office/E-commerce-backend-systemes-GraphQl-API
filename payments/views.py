
# Create your views here.
import hashlib
import hmac
import json

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order

from .models import CryptoTransaction, PaymentWebhookLog


@csrf_exempt
def nowpayments_ipn_webhook(request):
    """الاستقبال الآمن لإشعارات الدفع اللحظية من NOWPayments"""
    if request.method != 'POST':
        return HttpResponse(status=405)

    sig_header = request.headers.get('x-nowpayments-sig')
    raw_body = request.body

    # التحقق من الأمان عبر HMAC Signature
    ipn_secret = getattr(settings, 'NOWPAYMENTS_IPN_SECRET', '')
    is_verified = False

    if ipn_secret and sig_header:
        try:
            computed_sig = hmac.new(
                ipn_secret.encode('utf-8'),
                raw_body,
                hashlib.sha512
            ).hexdigest()
            if hmac.compare_digest(computed_sig, sig_header):
                is_verified = True
        except Exception:
            pass

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    payment_id = str(payload.get('payment_id'))
    payment_status = payload.get('payment_status')
    order_id = payload.get('order_id')

    # تسجيل الـ Webhook في قاعدة البيانات للتدقيق والمراجعة
    PaymentWebhookLog.objects.create(
        payment_id=payment_id,
        event_type=payment_status,
        payload=payload,
        is_verified=is_verified
    )

    # تحديث حالة المعاملة والطلب تلقائياً
    try:
        tx = CryptoTransaction.objects.get(payment_id=payment_id)
        tx.status = payment_status
        tx.actually_paid = payload.get('actually_paid', tx.actually_paid)
        tx.outcome_amount = payload.get('outcome_amount', tx.outcome_amount)
        tx.save()

        # إذا تم الدفع بنجاح وتأكيد المعاملة على البلوكشين
        if payment_status in ['finished', 'confirmed']:
            order = tx.order
            order.payment_status = Order.PaymentStatus.PAID
            order.status = Order.Status.PROCESSING
            order.save()

            # (اختياري): يمكنك هنا تفعيل إرسال الشحنة للمخزن أو توليد القيد المحاسبي

    except CryptoTransaction.DoesNotExist:
        pass

    return HttpResponse(status=200)