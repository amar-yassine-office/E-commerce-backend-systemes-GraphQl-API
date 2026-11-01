from django.contrib import admin

# Register your models here.
from .models import (
    InventoryStock,
    ReorderRule,
    StockAdjustment,
    StockLocation,
    StockMovement,
    Warehouse,
)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    search_fields = ('name', 'code')

@admin.register(StockLocation)
class StockLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'warehouse')
    list_filter = ('warehouse',)

@admin.register(InventoryStock)
class InventoryStockAdmin(admin.ModelAdmin):
    list_display = ('product_variant', 'warehouse', 'quantity_on_hand', 'quantity_reserved', 'available_quantity')
    list_filter = ('warehouse',)
    search_fields = ('product_variant__sku',)

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product_variant', 'warehouse', 'movement_type', 'quantity', 'reference', 'created_at')
    list_filter = ('movement_type', 'warehouse', 'created_at')
    search_fields = ('product_variant__sku', 'reference')

@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('product_variant', 'warehouse', 'system_quantity', 'actual_quantity', 'status', 'created_at')
    list_filter = ('status', 'warehouse')

@admin.register(ReorderRule)
class ReorderRuleAdmin(admin.ModelAdmin):
    list_display = ('product_variant', 'warehouse', 'min_stock_level', 'reorder_quantity')
    list_filter = ('warehouse',)