# inventory/services.py

# استيراد مهام Celery الخاصة بالمخزون
from .models import ProductVariant, StockAdjustment, Warehouse
from .tasks import check_low_stock_levels_task, process_stock_adjustment_task


class InventoryManagementService:

    @staticmethod
    def create_stock_adjustment(warehouse_id, product_variant_id, actual_quantity, system_quantity, reason):
        """
        خدمة لإنشاء طلب تسوية مخزنية وتشغيل مهمة المعالجة في الخلفية
        """
        warehouse = Warehouse.objects.get(id=warehouse_id)
        product_variant = ProductVariant.objects.get(id=product_variant_id)

        # إنشاء سجل التسوية بحالة معلقة
        adjustment = StockAdjustment.objects.create(
            warehouse=warehouse,
            product_variant=product_variant,
            system_quantity=system_quantity,
            actual_quantity=actual_quantity,
            reason=reason,
            status=StockAdjustment.Status.PENDING
        )

        # تشغيل مهمة Celery لمعالجة التسوية واعتمادها في الخلفية
        process_stock_adjustment_task.delay(adjustment.id)

        return adjustment

    @staticmethod
    def trigger_low_stock_check():
        """
        خدمة لتشغيل فحص المخزون المنخفض يدوياً أو جدولتها
        """
        check_low_stock_levels_task.delay()
        return "Low stock check task triggered successfully."