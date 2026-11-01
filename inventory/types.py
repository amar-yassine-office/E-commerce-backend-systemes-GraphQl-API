import strawberry
from typing import List, Optional

# استيراد النماذج
from inventory.models import (
    Warehouse, StockLocation, InventoryStock,
    StockMovement, StockAdjustment, ReorderRule
)

@strawberry.django.type(Warehouse)
class WarehouseType:
    id: strawberry.ID
    name: str
    code: str
    address: str
    is_active: bool


@strawberry.django.type(StockLocation)
class StockLocationType:
    id: strawberry.ID
    warehouse: WarehouseType
    name: str
    code: str


@strawberry.django.type(InventoryStock)
class InventoryStockType:
    id: strawberry.ID
    warehouse: WarehouseType
    # product_variant سيتم ربطه حسب نوع الـ ProductVariant Type لديك في الكتالوج
    quantity_on_hand: int
    quantity_reserved: int
    available_quantity: int


@strawberry.django.type(StockMovement)
class StockMovementType:
    id: strawberry.ID
    movement_type: str
    quantity: int
    reference: Optional[str]
    created_at: str


@strawberry.django.type(StockAdjustment)
class StockAdjustmentType:
    id: strawberry.ID
    warehouse: WarehouseType
    system_quantity: int
    actual_quantity: int
    reason: str
    status: str
    created_at: str


@strawberry.django.type(ReorderRule)
class ReorderRuleType:
    id: strawberry.ID
    warehouse: WarehouseType
    min_stock_level: int
    reorder_quantity: int


# --- Input Types للـ Mutations ---

@strawberry.input
class WarehouseInput:
    name: str
    code: str
    address: str
    is_active: Optional[bool] = True


@strawberry.input
class StockLocationInput:
    warehouse_id: int
    name: str
    code: str


@strawberry.input
class StockMovementInput:
    product_variant_id: int
    warehouse_id: int
    movement_type: str  # 'IN', 'OUT', 'TRANSFER'
    quantity: int
    reference: Optional[str] = None


@strawberry.input
class StockAdjustmentInput:
    warehouse_id: int
    product_variant_id: int
    system_quantity: int
    actual_quantity: int
    reason: str