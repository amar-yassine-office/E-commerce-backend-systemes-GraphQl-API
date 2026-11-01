# orders/services.py

from decimal import Decimal
from .tasks import process_new_order_task, process_fulfillment_dispatch_task, process_return_received_task
from .models import Order, OrderItem, OrderFulfillment, OrderFulfillmentItem, ReturnOrder, ReturnItem


class OrderManagementService:

    @staticmethod
    def create_order(customer_data, items_data, shipping_data, currency='USD'):
        """
        خدمة لإنشاء طلب جديد مع بنوده وحساب الإجماليات، ثم تشغيل مهمة معالجة المخزون في الخلفية
        """
        subtotal = Decimal('0.00')

        # حساب المجموع الفرعي من البنود
        for item in items_data:
            subtotal += item['unit_price'] * item['quantity']

        tax_total = subtotal * Decimal('0.10')  # مثال: ضريبة 10%
        shipping_total = shipping_data.get('shipping_total', Decimal('0.00'))
        discount_total = shipping_data.get('discount_total', Decimal('0.00'))
        grand_total = subtotal + tax_total + shipping_total - discount_total

        # إنشاء رأس الطلب (Master Order)
        order = Order.objects.create(
            customer_email=customer_data['email'],
            customer_name=customer_data['name'],
            customer_phone=customer_data.get('phone'),
            shipping_address=shipping_data['address'],
            shipping_city=shipping_data['city'],
            shipping_country=shipping_data['country'],
            postal_code=shipping_data.get('postal_code'),
            currency=currency,
            subtotal=subtotal,
            tax_total=tax_total,
            shipping_total=shipping_total,
            discount_total=discount_total,
            grand_total=grand_total
        )

        # إنشاء بنود الطلب (Order Items)
        for item_data in items_data:
            OrderItem.objects.create(
                order=order,
                product_variant=item_data['product_variant'],
                product_name=item_data['product_name'],
                sku=item_data['sku'],
                unit_price=item_data['unit_price'],
                quantity=item_data['quantity'],
                total_price=item_data['unit_price'] * item_data['quantity']
            )

        # تشغيل مهمة Celery لمعالجة الطلب وحجز المخزون في الخلفية
        process_new_order_task.delay(order.id)

        return order

    @staticmethod
    def create_fulfillment(order_id, warehouse_id, items_data, tracking_number=None, carrier_name=None):
        """
        خدمة لإنشاء شحنة جديدة للطلب وتشغيل مهمة تأكيد الشحن في الخلفية
        """
        order = Order.objects.get(id=order_id)

        fulfillment = OrderFulfillment.objects.create(
            order=order,
            warehouse_id=warehouse_id,
            tracking_number=tracking_number,
            carrier_name=carrier_name,
            status=OrderFulfillment.Status.PROCESSING
        )

        for item in items_data:
            OrderFulfillmentItem.objects.create(
                fulfillment=fulfillment,
                order_item_id=item['order_item_id'],
                quantity=item['quantity']
            )

        # تشغيل مهمة Celery لتأكيد الشحنة وخصم المخزون
        process_fulfillment_dispatch_task.delay(fulfillment.id)

        return fulfillment

    @staticmethod
    def create_return_order(order_id, reason, items_data):
        """
        خدمة لإنشاء طلب إرجاع (RMA) للعميل
        """
        return_order = ReturnOrder.objects.create(
            order_id=order_id,
            reason=reason,
            status=ReturnOrder.Status.REQUESTED
        )

        for item in items_data:
            ReturnItem.objects.create(
                return_order=return_order,
                order_item_id=item['order_item_id'],
                quantity=item['quantity'],
                condition=item.get('condition', 'سليم')
            )

        return return_order

    @staticmethod
    def mark_return_received(return_order_id):
        """
        خدمة لتحديث حالة استلام المرتجع وتشغيل مهمة إعادة البضاعة للمخزون
        """
        return_order = ReturnOrder.objects.get(id=return_order_id)
        return_order.status = ReturnOrder.Status.RECEIVED
        return_order.save()

        # تشغيل مهمة Celery لإدخال البضاعة للمخزون
        process_return_received_task.delay(return_order.id)

        return return_order