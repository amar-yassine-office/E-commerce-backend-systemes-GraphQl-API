from typing import List, Optional
from inventory.models import (
    Warehouse, StockLocation, InventoryStock,
    StockMovement, StockAdjustment, ReorderRule
)


class InventoryService:

    # --- المستودعات (Warehouses) ---
    @staticmethod
    def get_all_warehouses() -> List[Warehouse]:
        return Warehouse.objects.all()

    @staticmethod
    def create_warehouse(data: dict) -> Warehouse:
        return Warehouse.objects.create(**data)

    # --- مواقع التخزين (Stock Locations) ---
    @staticmethod
    def get_warehouse_locations(warehouse_id: int) -> List[StockLocation]:
        return StockLocation.objects.filter(warehouse_id=warehouse_id)

    @staticmethod
    def create_location(data: dict) -> StockLocation:
        return StockLocation.objects.create(**data)

    # --- أرصدة المخزون (Inventory Stock) ---
    @staticmethod
    def get_stock_by_warehouse(warehouse_id: int) -> List[InventoryStock]:
        return InventoryStock.objects.filter(warehouse_id=warehouse_id).select_related('warehouse')

    # --- حركات المخزون (Stock Movements) ---
    @staticmethod
    def create_stock_movement(data: dict) -> StockMovement:
        warehouse_id = data.get('warehouse_id')
        variant_id = data.get('product_variant_id')
        qty = data.get('quantity')
        movement_type = data.get('movement_type')

        # إنشاء سجل الحركة
        movement = StockMovement.objects.create(**data)

        # تحديث الرصيد الفعلي في InventoryStock تلقائياً
        stock, created = InventoryStock.objects.get_or_create(
            warehouse_id=warehouse_id,
            product_variant_id=variant_id,
            defaults={'quantity_on_hand': 0}
        )

        if movement_type == 'IN':
            stock.quantity_on_hand += qty
        elif movement_type == 'OUT':
            stock.quantity_on_hand -= qty

        stock.save()
        return movement

    # --- تسويات المخزون (Stock Adjustments) ---
    @staticmethod
    def create_adjustment(data: dict) -> StockAdjustment:
        return StockAdjustment.objects.create(**data)

    @staticmethod
    def approve_adjustment(adjustment_id: int) -> Optional[StockAdjustment]:
        try:
            adjustment = StockAdjustment.objects.get(pk=adjustment_id)
            if adjustment.status != StockAdjustment.Status.APPROVED:
                # تحديث الكمية الفعلية في المخزون بناءً على الجرد
                stock, _ = InventoryStock.objects.get_or_create(
                    warehouse=adjustment.warehouse,
                    product_variant=adjustment.product_variant
                )
                stock.quantity_on_hand = adjustment.actual_quantity
                stock.save()

                adjustment.status = StockAdjustment.Status.APPROVED
                adjustment.save()
            return adjustment
        except StockAdjustment.DoesNotExist:
            return None