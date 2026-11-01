import strawberry
from decimal import Decimal
from typing import List, Optional

from orders.models import Order, OrderItem, OrderFulfillment, OrderFulfillmentItem, ReturnOrder, ReturnItem
from catalog.types import ProductVariantType
from inventory.types import WarehouseType


@strawberry.django.type(Order)
class OrderType:
    id: strawberry.ID
    customer_email: str
    customer_name: str
    customer_phone: Optional[str]
    shipping_address: str
    shipping_city: str
    shipping_country: str
    postal_code: Optional[str]
    status: str
    payment_status: str
    fulfillment_status: str
    currency: str
    subtotal: Decimal
    tax_total: Decimal
    shipping_total: Decimal
    discount_total: Decimal
    grand_total: Decimal
    created_at: str
    updated_at: str

    # العلاقات
    items: List['OrderItemType']
    fulfillments: List['OrderFulfillmentType']
    returns: List['ReturnOrderType']


@strawberry.django.type(OrderItem)
class OrderItemType:
    id: strawberry.ID
    order: OrderType
    product_variant: ProductVariantType
    product_name: str
    sku: str
    unit_price: Decimal
    quantity: int
    total_price: Decimal


@strawberry.django.type(OrderFulfillment)
class OrderFulfillmentType:
    id: strawberry.ID
    order: OrderType
    warehouse: WarehouseType
    tracking_number: Optional[str]
    carrier_name: Optional[str]
    status: str
    shipped_at: Optional[str]
    created_at: str
    items: List['OrderFulfillmentItemType']


@strawberry.django.type(OrderFulfillmentItem)
class OrderFulfillmentItemType:
    id: strawberry.ID
    fulfillment: OrderFulfillmentType
    order_item: OrderItemType
    quantity: int


@strawberry.django.type(ReturnOrder)
class ReturnOrderType:
    id: strawberry.ID
    order: OrderType
    reason: str
    status: str
    created_at: str
    items: List['ReturnItemType']


@strawberry.django.type(ReturnItem)
class ReturnItemType:
    id: strawberry.ID
    return_order: ReturnOrderType
    order_item: OrderItemType
    quantity: int
    condition: Optional[str]


# --- Input Types للـ Mutations ---

@strawberry.input
class OrderItemInput:
    product_variant_id: int
    quantity: int
    unit_price: Decimal


@strawberry.input
class OrderInput:
    customer_email: str
    customer_name: str
    customer_phone: Optional[str] = None
    shipping_address: str
    shipping_city: str
    shipping_country: str
    postal_code: Optional[str] = None
    currency: Optional[str] = 'USD'
    subtotal: Decimal
    tax_total: Optional[Decimal] = Decimal('0.00')
    shipping_total: Optional[Decimal] = Decimal('0.00')
    discount_total: Optional[Decimal] = Decimal('0.00')
    grand_total: Decimal
    items: List[OrderItemInput]


@strawberry.input
class OrderFulfillmentItemInput:
    order_item_id: int
    quantity: int


@strawberry.input
class OrderFulfillmentInput:
    order_id: int
    warehouse_id: int
    tracking_number: Optional[str] = None
    carrier_name: Optional[str] = None
    items: List[OrderFulfillmentItemInput]


@strawberry.input
class ReturnItemInput:
    order_item_id: int
    quantity: int
    condition: Optional[str] = None


@strawberry.input
class ReturnOrderInput:
    order_id: int
    reason: str
    items: List[ReturnItemInput]