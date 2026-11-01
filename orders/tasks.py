from celery import shared_task
from django.db import transaction
from .models import Order, OrderFulfillment, ReturnOrder
from inventory.models import InventoryStock, StockMovement


@shared_task(bind=True, max_retries=3)
def process_new_order_task(self, order_id):
    """
    مهمة خلفية لمعالجة الطلب الجديد، حجز الكميات من المخزون، وتحديث الحالة
    """
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)

            if order.status == Order.Status.PROCESSING or order.status == Order.Status.COMPLETED:
                return f"Order #{order_id} is already processed."

            # المرور على بنود الطلب وحجز المخزون
            for item in order.items.all():
                # نفترض اختيار مستودع افتراضي أو بناءً على منطق التوجيه
                stock_record = InventoryStock.objects.select_for_update().filter(
                    product_variant=item.product_variant
                ).first()

                if stock_record:
                    # زيادة الكمية المحجوزة
                    stock_record.quantity_reserved += item.quantity
                    stock_record.save()

            # تحديث حالة الطلب إلى قيد المعالجة
            order.status = Order.Status.PROCESSING
            order.payment_status = Order.PaymentStatus.PAID
            order.save()

            return f"Successfully processed order and reserved inventory for Order #{order.id}"

    except Order.DoesNotExist:
        return "Order not found."
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)


@shared_task(bind=True, max_retries=3)
def process_fulfillment_dispatch_task(self, fulfillment_id):
    """
    مهمة خلفية لتأكيد شحنة الطلب، خصم المخزون الفعلي، وإنشاء حركات المخزون (صادر)
    """
    try:
        with transaction.atomic():
            fulfillment = OrderFulfillment.objects.select_for_update().get(id=fulfillment_id)

            if fulfillment.status == OrderFulfillment.Status.SHIPPED:
                return f"Fulfillment #{fulfillment_id} is already shipped."

            for f_item in fulfillment.items.all():
                order_item = f_item.order_item
                warehouse = fulfillment.warehouse

                stock_record = InventoryStock.objects.select_for_update().filter(
                    warehouse=warehouse,
                    product_variant=order_item.product_variant
                ).first()

                if stock_record:
                    # خصم الكمية من المخزون الفعلي والكمية المحجوزة
                    stock_record.quantity_on_hand -= f_item.quantity
                    stock_record.quantity_reserved = max(0, stock_record.quantity_reserved - f_item.quantity)
                    stock_record.save()

                    # تسجيل حركة مخزون صادر (OUT)
                    StockMovement.objects.create(
                        product_variant=order_item.product_variant,
                        warehouse=warehouse,
                        movement_type=StockMovement.MovementType.OUT,
                        quantity=f_item.quantity,
                        reference=f"FULFILLMENT-{fulfillment.id}"
                    )

            # تحديث حالة الشحنة
            fulfillment.status = OrderFulfillment.Status.SHIPPED
            fulfillment.save()

            # التحقق مما إذا تم شحن كامل الطلب لتحديث حالة الشحن للطلب الرئيسي
            order = fulfillment.order
            order.fulfillment_status = Order.FulfillmentStatus.FULFILLED
            order.save()

            return f"Successfully dispatched fulfillment #{fulfillment.id} for Order #{order.id}"

    except OrderFulfillment.DoesNotExist:
        return "Fulfillment record not found."
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)


@shared_task(bind=True, max_retries=3)
def process_return_received_task(self, return_order_id):
    """
    مهمة خلفية لمعالجة استلام المنتجات المرتجعة في المستودع وإعادتها للمخزون
    """
    try:
        with transaction.atomic():
            return_order = ReturnOrder.objects.select_for_update().get(id=return_order_id)

            if return_order.status == ReturnOrder.Status.RECEIVED:
                return f"Return #{return_order_id} is already processed."

            # افتراضياً نرجع البضاعة لأول مستودع متاح للبند أو مستودع رئيسي
            for ret_item in return_order.items.all():
                order_item = ret_item.order_item
                stock_record = InventoryStock.objects.select_for_update().filter(
                    product_variant=order_item.product_variant
                ).first()

                if stock_record:
                    # زيادة المخزون الفعلي بالبضاعة المرتجعة السليمة
                    stock_record.quantity_on_hand += ret_item.quantity
                    stock_record.save()

                    # تسجيل حركة مخزون وارد (IN) بسبب إرجاع
                    StockMovement.objects.create(
                        product_variant=order_item.product_variant,
                        warehouse=stock_record.warehouse,
                        movement_type=StockMovement.MovementType.IN,
                        quantity=ret_item.quantity,
                        reference=f"RMA-RETURN-{return_order.id}"
                    )

            return_order.status = ReturnOrder.Status.RECEIVED
            return_order.save()

            return f"Successfully processed return items and updated stock for Return #{return_order.id}"

    except ReturnOrder.DoesNotExist:
        return "Return order not found."
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)