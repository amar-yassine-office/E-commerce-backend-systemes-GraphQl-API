from django.contrib import admin
from .models import (
    CryptoCurrency,
    CryptoTransaction,
    PaymentWebhookLog,
    CryptoPayout,
)


@admin.register(CryptoCurrency)
class CryptoCurrencyAdmin(admin.ModelAdmin):
    list_display = ("currency_code", "name", "is_active", "min_amount", "max_amount")
    list_filter = ("is_active",)
    search_fields = ("currency_code", "name")
    list_editable = ("is_active", "min_amount")


@admin.register(CryptoTransaction)
class CryptoTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "payment_id",
        "order",
        "pay_currency",
        "pay_amount",
        "price_amount",
        "price_currency",
        "status",
        "created_at",
    )
    list_filter = ("status", "pay_currency", "price_currency", "created_at")
    search_fields = ("payment_id", "invoice_id", "order__id", "pay_address")
    readonly_fields = ("payment_id", "created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(PaymentWebhookLog)
class PaymentWebhookLogAdmin(admin.ModelAdmin):
    list_display = ("id", "payment_id", "event_type", "is_verified", "received_at")
    list_filter = ("is_verified", "received_at")
    search_fields = ("payment_id", "event_type")
    readonly_fields = ("payment_id", "event_type", "payload", "is_verified", "received_at")
    date_hierarchy = "received_at"


@admin.register(CryptoPayout)
class CryptoPayoutAdmin(admin.ModelAdmin):
    list_display = (
        "payout_id",
        "crypto_transaction",
        "currency",
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "currency", "created_at")
    search_fields = ("payout_id", "address", "currency")
    readonly_fields = ("payout_id", "created_at")
    date_hierarchy = "created_at"