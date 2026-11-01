import strawberry
from decimal import Decimal
from strawberry.types import Info
from .services import ShippingService


@strawberry.input
class CalculateShippingInput:
    zone_id: strawberry.ID
    method_id: strawberry.ID
    weight: Decimal
    order_amount: Decimal


@strawberry.type
class ShippingMutation:
    @strawberry.mutation
    def calculate_shipping_cost(self, info: Info, input: CalculateShippingInput) -> Decimal:
        """حساب تكلفة الشحن للطلب الحالي بناءً على المدخلات."""
        return ShippingService.calculate_shipping_cost(
            zone_id=int(input.zone_id),
            method_id=int(input.method_id),
            weight=input.weight,
            order_amount=input.order_amount,
        )