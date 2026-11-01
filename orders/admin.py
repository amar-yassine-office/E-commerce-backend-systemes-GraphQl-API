from django.contrib import admin

# Register your models here.
from .models import (
    Order,
    OrderFulfillment,
    OrderItem,
    ReturnOrder,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)

class OrderFulfillmentInline(admin.TabularInline):
    model = OrderFulfillment
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'grand_total', 'currency', 'status', 'payment_status', 'fulfillment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'fulfillment_status', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'id')
    inlines = [OrderItemInline, OrderFulfillmentInline]

@admin.register(OrderFulfillment)
class OrderFulfillmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'warehouse', 'carrier_name', 'tracking_number', 'status', 'shipped_at')
    list_filter = ('status', 'warehouse')

@admin.register(ReturnOrder)
class ReturnOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'status', 'created_at')
    list_filter = ('status',)