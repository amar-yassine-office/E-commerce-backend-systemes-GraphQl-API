import strawberry
import strawberry_django
from typing import List
from strawberry.types import Info
from .types import (
    ShippingZoneType,
    ShippingCarrierType,
    ShippingMethodType,
    ShippingRateType,
)
from .cache import ShippingCacheService
from .models import ShippingRate


@strawberry.type
class ShippingQuery:
    @strawberry.field
    def active_shipping_zones(self, info: Info) -> List[ShippingZoneType]:
        """جلب مناطق الشحن النشطة من الكاش."""
        return ShippingCacheService.get_cached_active_zones()

    @strawberry.field
    def active_shipping_carriers(self, info: Info) -> List[ShippingCarrierType]:
        """جلب شركات الشحن النشطة من الكاش."""
        return ShippingCacheService.get_cached_active_carriers()

    @strawberry.field
    def active_shipping_methods(self, info: Info) -> List[ShippingMethodType]:
        """جلب طرق الشحن المتاحة عبر الكاش."""
        return ShippingCacheService.get_cached_active_methods()

    # استعلامات مباشرة للأسعار مع دعم الفلترة
    shipping_rates: List[ShippingRateType] = strawberry_django.field()