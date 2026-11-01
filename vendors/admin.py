from django.contrib import admin

# Register your models here.
from .models import PurchaseOrder, PurchaseOrderItem, Vendor, VendorBill


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'email', 'phone', 'currency', 'is_active')
    list_filter = ('is_active', 'currency')
    search_fields = ('name', 'code', 'email')

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    readonly_fields = ('total_price',)

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor', 'warehouse', 'status', 'order_date', 'expected_delivery_date', 'grand_total')
    list_filter = ('status', 'warehouse', 'order_date')
    search_fields = ('vendor__name', 'id')
    inlines = [PurchaseOrderItemInline]

@admin.register(VendorBill)
class VendorBillAdmin(admin.ModelAdmin):
    list_display = ('bill_number', 'vendor', 'purchase_order', 'status', 'bill_date', 'due_date', 'grand_total')
    list_filter = ('status', 'bill_date')
    search_fields = ('bill_number', 'vendor__name')