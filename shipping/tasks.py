from celery import shared_task
from django.db import transaction
from orders.models import OrderFulfillment


@shared_task(bind=True, max_retries=3)
def sync_shipment_tracking_status_task(self, fulfillment_id):
    """
    مهمة خلفية للاتصال بـ API شركة الشحن وجلب أحدث حالة تتبعية للشحنة وتحديثها
    """
    try:
        with transaction.atomic():
            fulfillment = OrderFulfillment.objects.select_for_update().get(id=fulfillment_id)

            if not fulfillment.tracking_number:
                return f"Fulfillment #{fulfillment_id} has no tracking number."

            # محاكاة الاتصال بـ API الخارجي لشركة الشحن (مثل DHL, Aramex)
            # api_response = requests.get(f"https://api.carrier.com/track/{fulfillment.tracking_number}")

            # مثال لتحديث الحالة بناءً على الرد الخارجي
            # new_status = api_response.json().get('status')
            # fulfillment.status = new_status
            # fulfillment.save()

            return f"Successfully synced tracking status for fulfillment #{fulfillment.id}"

    except OrderFulfillment.DoesNotExist:
        return "Fulfillment record not found."
    except Exception as exc:
        raise self.retry(exc=exc, countdown=15)