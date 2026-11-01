# vendors/services.py

from decimal import Decimal
from .tasks import process_purchase_order_receipt_task, check_overdue_vendor_bills_task
from .models import PurchaseOrder, PurchaseOrderItem, VendorBill


class VendorManagementService:

    @staticmethod
    def create_purchase_order(vendor_id, warehouse_id, order_date, items_data, expected_delivery_date=None, notes=None):
        """
        خدمة لإنشاء أمر شراء جديد مع بنوده وحساب الإجماليات المالية بدقة
        """
        subtotal = Decimal('0.00')

        for item in items_data:
            subtotal += item['unit_price'] * item['quantity_ordered']

        tax_total = subtotal * Decimal('0.15')  # مثال: ضريبة القيمة المضافة 15%
        grand_total = subtotal + tax_total

        # إنشاء رأس أمر الشراء
        po = PurchaseOrder.objects.create(
            vendor_id=vendor_id,
            warehouse_id=warehouse_id,
            order_date=order_date,
            expected_delivery_date=expected_delivery_date,
            status=PurchaseOrder.Status.DRAFT,
            subtotal=subtotal,
            tax_total=tax_total,
            grand_total=grand_total,
            notes=notes
        )

        # إنشاء بنود أمر الشراء
        for item_data in items_data:
            q_ordered = item_data['quantity_ordered']
            u_price = item_data['unit_price']
            PurchaseOrderItem.objects.create(
                purchase_order=po,
                product_variant=item_data['product_variant'],
                quantity_ordered=q_ordered,
                quantity_received=item_data.get('quantity_received', 0),
                unit_price=u_price,
                total_price=u_price * q_ordered
            )

        return po

    @staticmethod
    def receive_purchase_order(purchase_order_id, items_received_data=None):
        """
        خدمة لتسجيل استلام البضائع في المستودع وتشغيل مهمة تحديث المخزون وحركات الوارد في الخلفية
        """
        po = PurchaseOrder.objects.get(id=purchase_order_id)

        if items_received_data:
            for data in items_received_data:
                item = PurchaseOrderItem.objects.get(id=data['item_id'], purchase_order=po)
                item.quantity_received = data['quantity_received']
                item.save()

        # تشغيل مهمة Celery للمعالجة الآمنة وتحديث المخزون
        process_purchase_order_receipt_task.delay(po.id)

        return po

    @staticmethod
    def trigger_overdue_bills_check():
        """
        خدمة لتشغيل مهمة فحص فواتير الموردين المتأخرة يدوياً
        """
        check_overdue_vendor_bills_task.delay()
        return "Overdue vendor bills check task triggered successfully."