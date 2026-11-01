import strawberry
from typing import List
from inventory.types import WarehouseType, StockLocationType, InventoryStockType, StockMovementType
from inventory.services import InventoryService

@strawberry.type
class Query:

    @strawberry.field
    def warehouses(self) -> List[WarehouseType]:
        """استرجاع قائمة جميع المستودعات"""
        return InventoryService.get_all_warehouses()

    @strawberry.field
    def warehouse_locations(self, warehouse_id: int) -> List[StockLocationType]:
        """استرجاع مواقع التخزين داخل مستودع محدد"""
        return InventoryService.get_warehouse_locations(warehouse_id)

    @strawberry.field
    def inventory_stocks(self, warehouse_id: int) -> List[InventoryStockType]:
        """استرجاع أرصدة المخزون لمستودع معين"""
        return InventoryService.get_stock_by_warehouse(warehouse_id)