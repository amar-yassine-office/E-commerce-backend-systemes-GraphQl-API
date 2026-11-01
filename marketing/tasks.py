from celery import shared_task
from django.utils import timezone
from django.db import transaction
from .models import Coupon, Promotion, LoyaltyTransaction, Customer


@shared_task(bind=True)
def update_marketing_campaigns_status_task(self):
    """
    مهمة خلفية دورية للتحقق من تواريخ البداية والنهاية وتحديث حالة الحملات والكوبونات (تنشيط أو إيقاف)
    """
    try:
        now = timezone.now()

        # 1. إيقاف الحملات الترويجية التي انتهى تاريخها
        expired_promotions = Promotion.objects.filter(is_active=True, end_date__lt=now)
        expired_promotions.update(is_active=False)

        # 2. تنشيط الحملات التي حان موعد بدايتها
        starting_promotions = Promotion.objects.filter(is_active=False, start_date__lte=now, end_date__gte=now)
        starting_promotions.update(is_active=True)

        # 3. إيقاف الكوبونات منتهية الصلاحية
        expired_coupons = Coupon.objects.filter(is_active=True, end_date__lt=now)
        expired_coupons.update(is_active=False)

        return f"Successfully updated marketing campaigns and coupons status at {now}."

    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


@shared_task(bind=True, max_retries=3)
def award_loyalty_points_task(self, customer_id, order_id, points_amount, notes=None):
    """
    مهمة خلفية لإضافة نقاط ولاء للعميل بعد إتمام الطلب بنجاح بشكل آمن
    """
    try:
        with transaction.atomic():
            customer = Customer.objects.select_for_update().get(id=customer_id)

            # تسجيل حركة نقاط الولاء
            LoyaltyTransaction.objects.create(
                customer=customer,
                order_id=order_id,
                transaction_type=LoyaltyTransaction.TransactionType.EARNED,
                points=points_amount,
                notes=notes or "نقاط مكتسبة من إتمام الطلب"
            )

            return f"Successfully awarded {points_amount} points to customer: {customer.user.email}"

    except Customer.DoesNotExist:
        return "Customer not found."
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)