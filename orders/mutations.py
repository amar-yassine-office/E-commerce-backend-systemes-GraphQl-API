import strawberry
from orders.types import OrderType, OrderFulfillmentType, ReturnOrderType, OrderInput, OrderFulfillmentInput, \
    ReturnOrderInput
from orders.services import OrderService


@strawberry.type
class Mutation:

    @strawberry.mutation
    def create_order(self, input: OrderInput) -> OrderType:
        """إنشاء طلب شراء جديد مع البنود الخاصة به"""
        items_data = [
            {
                "product_variant_id": item.product_variant_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
            }
            for item in input.items
        ]

        order_data = {
            "customer_email": input.customer_email,
            "customer_name": input.customer_name,
            "customer_phone": input.customer_phone,
            "shipping_address": input.shipping_address,
            "shipping_city": input.shipping_city,
            "shipping_country": input.shipping_country,
            "postal_code": input.postal_code,
            "currency": input.currency,
            "subtotal": input.subtotal,
            "tax_total": input.tax_total,
            "shipping_total": input.shipping_total,
            "discount_total": input.discount_total,
            "grand_total": input.grand_total,
        }

        return OrderService.create_order(order_data, items_data)

    @strawberry.mutation
    def create_order_fulfillment(self, input: OrderFulfillmentInput) -> OrderFulfillmentType:
        """إنشاء شحنة جديدة لتنفيذ الطلب من مستودع معين"""
        data = {
            "order_id": input.order_id,
            "warehouse_id": input.warehouse_id,
            "tracking_number": input.tracking_number,
            "carrier_name": input.carrier_name,
        }
        items_data = [
            {
                "order_item_id": item.order_item_id,
                "quantity": item.quantity,
            }
            for item in input.items
        ]
        return OrderService.create_fulfillment(data, items_data)

    @strawberry.mutation
    def create_return_order(self, input: ReturnOrderInput) -> ReturnOrderType:
        """تقديم طلب إرجاع (RMA) لبنود داخل الطلب"""
        data = {
            "order_id": input.order_id,
            "reason": input.reason,
        }
        items_data = [
            {
                "order_item_id": item.order_item_id,
                "quantity": item.quantity,
                "condition": item.condition,
            }
            for item in input.items
        ]
        return OrderService.create_return_order(data, items_data)