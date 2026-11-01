from typing import List, Optional
from django.db import transaction
from orders.models import Order, OrderItem, OrderFulfillment, OrderFulfillmentItem, ReturnOrder, ReturnItem
from catalog.models import ProductVariant


class OrderService:

    # --- استعلامات الطلبات ---
    @staticmethod
    def get_all_orders() -> List[Order]:
        return Order.objects.prefetch_related('items__product_variant', 'fulfillments', 'returns').all()

    @staticmethod
    def get_order_by_id(order_id: int) -> Optional[Order]:
        try:
            return Order.objects.prefetch_related('items__product_variant', 'fulfillments__items',
                                                  'returns__items').get(pk=order_id)
        except Order.DoesNotExist:
            return None

    # --- إنشاء طلب جديد مع بنوده ---
    @staticmethod
    @transaction.atomic
    def create_order(data: dict, items_data: list) -> Order:
        order = Order.objects.create(**data)

        for item_data in items_data:
            variant_id = item_data.get('product_variant_id')
            variant = ProductVariant.objects.get(pk=variant_id)

            quantity = item_data.get('quantity')
            unit_price = item_data.get('unit_price')
            total_price = unit_price * quantity

            OrderItem.objects.create(
                order=order,
                product_variant=variant,
                product_name=variant.product.name,  # افتراض وجود اسم المنتج عبر العلاقة
                sku=variant.sku,
                unit_price=unit_price,
                quantity=quantity,
                total_price=total_price
            )
        return order

    # --- تجهيز وشحن الطلب (Fulfillment) ---
    @staticmethod
    @transaction.atomic
    def create_fulfillment(data: dict, items_data: list) -> OrderFulfillment:
        order_id = data.get('order_id')
        warehouse_id = data.get('warehouse_id')

        fulfillment = OrderFulfillment.objects.create(
            order_id=order_id,
            warehouse_id=warehouse_id,
            tracking_number=data.get('tracking_number'),
            carrier_name=data.get('carrier_name'),
            status=OrderFulfillment.Status.PROCESSING
        )

        for item in items_data:
            OrderFulfillmentItem.objects.create(
                fulfillment=fulfillment,
                order_item_id=item.get('order_item_id'),
                quantity=item.get('quantity')
            )

        return fulfillment

    # --- إدارة المرتجعات (RMA) ---
    @staticmethod
    @transaction.atomic
    def create_return_order(data: dict, items_data: list) -> ReturnOrder:
        return_order = ReturnOrder.objects.create(
            order_id=data.get('order_id'),
            reason=data.get('reason'),
            status=ReturnOrder.Status.REQUESTED
        )

        for item in items_data:
            ReturnItem.objects.create(
                return_order=return_order,
                order_item_id=item.get('order_item_id'),
                quantity=item.get('quantity'),
                condition=item.get('condition')
            )

        return return_order