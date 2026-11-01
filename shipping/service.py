# shipping/services.py

from decimal import Decimal
from .tasks import sync_shipment_tracking_status_task
from .models import ShippingZone, ShippingRate


class ShippingManagementService:

    @staticmethod
    def calculate_shipping_cost(country_code: str, order_weight: Decimal, order_amount: Decimal):
        """
        خدمة ديناميكية لاحتساب تكلفة الشحن المناسبة بناءً على دولة الوجهة، وزن المنتجات، وقيمة الطلب
        """
        # 1. البحث عن منطقة الشحن المطابقة لدولة العميل
        zones = ShippingZone.objects.filter(is_active=True)
        matching_zone = None

        for zone in zones:
            countries_list = [c.strip().upper() for c in zone.countries.split(',')]
            if country_code.upper() in countries_list:
                matching_zone = zone
                break

        if not matching_zone:
            # إذا لم توجد منطقة مطابقة، نرجع تكلفة افتراضية أو صفرية
            return Decimal('0.00'), None

        # 2. البحث عن جدول الأسعار (ShippingRate) المطابق للوزن وقيمة الطلب داخل المنطقة
        rate = ShippingRate.objects.filter(
            zone=matching_zone,
            min_weight__lte=order_weight,
            max_weight__gte=order_weight,
            min_order_amount__lte=order_amount,
            max_order_amount__gte=order_amount,
            method__is_active=True
        ).first()

        if rate:
            return rate.base_cost, rate.method

        return Decimal('0.00'), None

    @staticmethod
    def trigger_tracking_sync(fulfillment_id: int):
        """
        خدمة لتشغيل مهمة مزامنة حالة التتبع للشحنة يدوياً أو جدولتها في الخلفية
        """
        sync_shipment_tracking_status_task.delay(fulfillment_id)
        return "Shipping tracking synchronization task triggered successfully."