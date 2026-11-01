from decimal import Decimal
from .cache import ShippingCacheService
from .models import ShippingRate


class ShippingService:
    """خدمة حساب وتحديد خيارات وأسعار الشحن المتاحة."""

    @staticmethod
    def get_available_shipping_methods():
        """جلب طرق الشحن المتاحة النشطة عبر الكاش."""
        return ShippingCacheService.get_cached_active_methods()

    @staticmethod
    def calculate_shipping_cost(zone_id: int, method_id: int, weight: Decimal, order_amount: Decimal) -> Decimal:
        """
        حساب تكلفة الشحن بدقة بناءً على القواعد والنوع (ثابت، حسب الوزن، أو حسب قيمة الطلب).
        """
        rate = ShippingRate.objects.filter(
            zone_id=zone_id,
            method_id=method_id,
            min_weight__lte=weight,
            max_weight__gte=weight,
            min_order_amount__lte=order_amount,
            max_order_amount__gte=order_amount
        ).first()

        if not rate:
            raise ValueError("No matching shipping rate found for the given criteria.")

        # حساب التكلفة بناءً على نوع التسعير
        if rate.pricing_type == ShippingRate.PricingType.FLAT_RATE:
            return rate.base_cost

        elif rate.pricing_type == ShippingRate.PricingType.WEIGHT_BASED:
            # مثال حسابي بسيط يعتمد على الوزن الأساسي المحدّد
            return rate.base_cost * weight

        elif rate.pricing_type == ShippingRate.PricingType.PRICE_BASED:
            # إذا كان التسعير يعتمد على قيمة الطلب
            return rate.base_cost

        return rate.base_cost