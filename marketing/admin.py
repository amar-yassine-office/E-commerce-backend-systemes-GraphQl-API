from django.contrib import admin

# Register your models here.
from .models import Coupon, GiftCard, LoyaltyTransaction, Promotion


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_order_amount', 'times_used', 'usage_limit', 'is_active', 'end_date')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code',)

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_type', 'discount_value', 'is_active', 'start_date', 'end_date')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('name',)
    filter_horizontal = ('customer_groups', 'categories', 'product_variants')

@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    list_display = ('code', 'initial_balance', 'current_balance', 'customer', 'is_active', 'expires_at')
    list_filter = ('is_active',)
    search_fields = ('code', 'customer__user__email')

@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'transaction_type', 'points', 'order', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('customer__user__email', 'order__id')
    # those the costunazation of the admin page
    admin.site.site_header= 'Ecommerce'
    admin.site.site_title = 'Ecommerce'