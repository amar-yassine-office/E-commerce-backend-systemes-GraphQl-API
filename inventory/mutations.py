import strawberry
from inventory.types import (
    WarehouseType, StockLocationType, StockMovementType, StockAdjustmentType,
    WarehouseInput, StockLocationInput, StockMovementInput, StockAdjustmentInput
)
from inventory.services import InventoryService

@strawberry.type
class Mutation:

    @strawberry.mutation
    def create_warehouse(self, input: WarehouseInput) -> WarehouseType:
        """إنشاء مستودع رئيسي جديد"""
        data = {
            "name": input.name,
            "code": input.code,
            "address": input.address,
            "is_active": input.is_active,
        }
        return InventoryService.create_warehouse(data)

    @strawberry.mutation
    def create_stock_location(self, input: StockLocationInput) -> StockLocationType:
        """إضافة موقع تخزين جديد داخل المستودع"""
        data = {
            "warehouse_id": input.warehouse_id,
            "name": input.name,
            "code": input.code,
        }
        return InventoryService.create_location(data)

    @strawberry.mutation
    def create_stock_movement(self, input: StockMovementInput) -> StockMovementType:
        """تسجيل حركة مخزنية جديدة (وارد، صادر، تحويل) وتحديث الرصيد تلقائياً"""
        data = {
            "product_variant_id": input.product_variant_id,
            "warehouse_id": input.warehouse_id,
            "movement_type": input.movement_type,
            "quantity": input.quantity,
            "reference": input.reference,
        }
        return InventoryService.create_stock_movement(data)

    @strawberry.mutation
    def create_stock_adjustment(self, input: StockAdjustmentInput) -> StockAdjustmentType:
        """إنشاء طلب تسوية جرد يدوي"""
        data = {
            "warehouse_id": input.warehouse_id,
            "product_variant_id": input.product_variant_id,
            "system_quantity": input.system_quantity,
            "actual_quantity": input.actual_quantity,
            "reason": input.reason,
        }
        return InventoryService.create_adjustment(data)

    @strawberry.mutation
    def approve_stock_adjustment(self, adjustment_id: int) -> StockAdjustmentType:
        """اعتماد تسوية المخزون وتحديث الكميات الفعلية في المستودع"""
        return InventoryService.approve_adjustment(adjustment_id)