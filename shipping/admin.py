from django.contrib import admin

# Register your models here.
from .models import ShippingCarrier, ShippingMethod, ShippingRate, ShippingZone


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'countries', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'countries')

@admin.register(ShippingCarrier)
class ShippingCarrierAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'carrier', 'is_active')
    list_filter = ('is_active', 'carrier')
    search_fields = ('name',)

@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ('method', 'zone', 'pricing_type', 'base_cost', 'min_weight', 'max_weight')
    list_filter = ('pricing_type', 'zone', 'method')