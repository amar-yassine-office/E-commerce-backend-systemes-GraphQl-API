from celery import shared_task
from django.db import transaction

from .models import InventoryStock, ReorderRule, StockAdjustment, StockMovement


@shared_task(bind=True, max_retries=3)
def process_stock_adjustment_task(self, adjustment_id):
    """
    مهمة خلفية لمعالجة واعتماد تسوية المخزون (عجز أو تلف) وتحديث الأرصدة وحركات المخزون بشكل آمن
    """
    try:
        with transaction.atomic():
            adjustment = StockAdjustment.objects.select_for_update().get(id=adjustment_id)

            if adjustment.status == StockAdjustment.Status.APPROVED:
                return f"Adjustment #{adjustment_id} is already approved."

            # 1. جلب أو إنشاء رصيد المخزون للمنتج في المستودع
            stock_record, _ = InventoryStock.objects.get_or_create(
                warehouse=adjustment.warehouse,
                product_variant=adjustment.product_variant,
                defaults={'quantity_on_hand': 0, 'quantity_reserved': 0}
            )

            # 2. حساب الفرق لتحديد نوع الحركة (وارد أو صادر)
            diff = adjustment.actual_quantity - stock_record.quantity_on_hand

            if diff != 0:
                movement_type = StockMovement.MovementType.IN if diff > 0 else StockMovement.MovementType.OUT

                # إنشاء سجل حركة المخزون
                StockMovement.objects.create(
                    product_variant=adjustment.product_variant,
                    warehouse=adjustment.warehouse,
                    movement_type=movement_type,
                    quantity=abs(diff),
                    reference=f"ADJUSTMENT-{adjustment.id}"
                )

                # تحديث الكمية الفعلية في المخزون
                stock_record.quantity_on_hand = adjustment.actual_quantity
                stock_record.save()

            # 3. اعتماد التسوية
            adjustment.status = StockAdjustment.Status.APPROVED
            adjustment.save()

            return f"Successfully processed stock adjustment for SKU: {adjustment.product_variant.sku}"

    except StockAdjustment.DoesNotExist:
        return "Stock adjustment record not found."
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)


@shared_task(bind=True)
def check_low_stock_levels_task(self):
    """
    مهمة خلفية دورية لفحص قواعد إعادة الطلب وتنبيه الإدارة عند انخفاض المخزون عن الحد الأدنى
    """
    try:
        rules = ReorderRule.objects.select_related('warehouse', 'product_variant').all()
        low_stock_items = []

        for rule in rules:
            stock_record = InventoryStock.objects.filter(
                warehouse=rule.warehouse,
                product_variant=rule.product_variant
            ).first()

            current_qty = stock_record.quantity_on_hand if stock_record else 0

            if current_qty <= rule.min_stock_level:
                low_stock_items.append({
                    'warehouse': rule.warehouse.name,
                    'sku': rule.product_variant.sku,
                    'current_quantity': current_qty,
                    'min_level': rule.min_stock_level,
                    'suggested_reorder': rule.reorder_quantity
                })
                # هنا يمكنك استدعاء خدمة إرسال إشعار أو بريد إلكتروني للمسؤولين

        return f"Checked {rules.count()} reorder rules. Found {len(low_stock_items)} low stock items."

    except Exception as exc:
        raise self.retry(exc=exc, countdown=15)