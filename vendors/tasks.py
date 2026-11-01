from celery import shared_task
from django.db import transaction
from django.utils import timezone
from .models import PurchaseOrder, VendorBill
from inventory.models import InventoryStock, StockMovement


@shared_task(bind=True, max_retries=3)
def process_purchase_order_receipt_task(self, purchase_order_id):
    """
    مهمة خلفية لمعالجة استلام أمر الشراء في المستودع، تحديث المخزون الفعلي، وإنشاء حركات المخزون الواردة (IN)
    """
    try:
        with transaction.atomic():
            po = PurchaseOrder.objects.select_for_update().get(id=purchase_order_id)

            if po.status == PurchaseOrder.Status.RECEIVED:
                return f"Purchase Order #{purchase_order_id} is already received."

            warehouse = po.warehouse

            for item in po.items.all():
                # جلب أو إنشاء سجل رصيد المخزون للمنتج في المستودع المحدد
                stock_record, _ = InventoryStock.objects.select_for_update().get_or_create(
                    warehouse=warehouse,
                    product_variant=item.product_variant,
                    defaults={'quantity_on_hand': 0, 'quantity_reserved': 0}
                )

                # تحديد الكمية الفعلية المضافة (المستلامة أو المطلوبة في حال لم تُحدد المستلامة)
                qty_to_add = item.quantity_received if item.quantity_received > 0 else item.quantity_ordered

                # تحديث الكمية الفعلية في المخزون
                stock_record.quantity_on_hand += qty_to_add
                stock_record.save()

                # تسجيل حركة مخزون وارد (IN)
                StockMovement.objects.create(
                    product_variant=item.product_variant,
                    warehouse=warehouse,
                    movement_type=StockMovement.MovementType.IN,
                    quantity=qty_to_add,
                    reference=f"PO-{po.id}"
                )

            # تحديث حالة أمر الشراء إلى تم الاستلام
            po.status = PurchaseOrder.Status.RECEIVED
            po.save()

            return f"Successfully processed receipt for Purchase Order #{po.id} and updated inventory."

    except PurchaseOrder.DoesNotExist:
        return "Purchase order not found."
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)


@shared_task(bind=True)
def check_overdue_vendor_bills_task(self):
    """
    مهمة خلفية دورية لفحص فواتير الموردين وتحديث حالة الفواتير التي تجاوزت تاريخ الاستحقاق إلى (متأخرة)
    """
    try:
        today = timezone.now().date()

        # البحث عن الفواتير غير المدفوعة والتي تجاوز تاريخ استحقاقها اليوم
        overdue_bills = VendorBill.objects.filter(
            status__in=[VendorBill.Status.DRAFT, VendorBill.Status.POSTED],
            due_date__lt=today
        )

        updated_count = overdue_bills.update(status=VendorBill.Status.OVERDUE)

        return f"Successfully checked vendor bills. Marked {updated_count} bills as overdue."

    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)