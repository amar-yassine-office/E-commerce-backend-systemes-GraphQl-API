from celery import shared_task
from django.core.cache import cache

from .models import Customer, CustomerGroup


@shared_task(bind=True, max_retries=3)
def send_welcome_notification_task(self, customer_id):
    """
    مهمة خلفية لإرسال إشعار أو بريد إلكتروني ترحيبي للعميل الجديد
    """
    try:
        customer = Customer.objects.get(id=customer_id)
        # محاكاة إرسال بريد إلكتروني ترحيبي أو إشعار تسويقي
        # send_mail(...)

        return f"Successfully sent welcome notification to customer: {customer.user.email}"

    except Customer.DoesNotExist:
        return "Customer not found."
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)


@shared_task(bind=True)
def update_customer_group_cache_task(self, group_id):
    """
    مهمة خلفية لمسح الكاش وتحديث صلاحيات أو خصومات الأسعار للعملاء التابعين لفئة معينة
    """
    try:
        group = CustomerGroup.objects.get(id=group_id)
        # مسح الكاش المؤقت لأسعار فئة العملاء لتطبيق نسب الخصم الجديدة فوراً
        cache.delete(f"customer_group_discount_{group.id}")

        return f"Successfully updated cache for Customer Group: {group.name}"

    except CustomerGroup.DoesNotExist:
        return "Customer Group not found."
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)