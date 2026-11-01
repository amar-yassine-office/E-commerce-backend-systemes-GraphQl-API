import strawberry
import strawberry_django
from decimal import Decimal
from .models import ShippingZone, ShippingCarrier, ShippingMethod, ShippingRate

@strawberry_django.type(ShippingZone)
class ShippingZoneType:
    id: strawberry.ID
    name: str
    countries: str
    is_active: bool


@strawberry_django.type(ShippingCarrier)
class ShippingCarrierType:
    id: strawberry.ID
    name: str
    code: str
    tracking_url_template: str | None
    is_active: bool


@strawberry_django.type(ShippingMethod)
class ShippingMethodType:
    id: strawberry.ID
    carrier: ShippingCarrierType
    name: str
    description: str | None
    is_active: bool


@strawberry_django.type(ShippingRate)
class ShippingRateType:
    id: strawberry.ID
    method: ShippingMethodType
    zone: ShippingZoneType
    pricing_type: str
    base_cost: Decimal
    min_weight: Decimal
    max_weight: Decimal
    min_order_amount: Decimal
    max_order_amount: Decimal