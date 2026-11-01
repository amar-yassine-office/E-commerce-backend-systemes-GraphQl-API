from django.contrib import admin
from .models import (
    ChartOfAccount,
    CryptoTransaction,
    Currency,
    JournalEntry,
    JournalItem,
    TaxRecord,
    VendorPayout,
)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "symbol", "exchange_rate_to_base", "is_active")
    list_editable = ("exchange_rate_to_base", "is_active")
    search_fields = ("code", "name")


@admin.register(ChartOfAccount)
class ChartOfAccountAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "account_type", "sub_type", "currency", "is_active")
    list_filter = ("account_type", "sub_type", "currency", "is_active")
    search_fields = ("code", "name")
    ordering = ("code",)


class JournalItemInline(admin.TabularInline):
    model = JournalItem
    extra = 2
    fields = ("account", "debit", "credit", "memo")
    autocomplete_fields = ["account"]


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = (
        "entry_number",
        "date",
        "source_module",
        "currency",
        "order",
        "vendor",
        "is_posted",
        "created_at",
    )
    list_filter = ("source_module", "is_posted", "currency", "date")
    search_fields = ("entry_number", "description", "order__id", "vendor__name")
    inlines = [JournalItemInline]
    readonly_fields = ("id", "created_at", "updated_at")
    date_hierarchy = "date"


@admin.register(CryptoTransaction)
class CryptoTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "nowpayments_id",
        "order",
        "payment_status",
        "price_amount",
        "price_currency",
        "pay_amount",
        "pay_currency",
        "actually_paid",
        "created_at",
    )
    list_filter = ("payment_status", "pay_currency", "price_currency", "created_at")
    search_fields = (
        "nowpayments_id",
        "invoice_id",
        "order__id",
        "pay_address",
    )
    readonly_fields = ("id", "nowpayments_id", "created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(TaxRecord)
class TaxRecordAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "country_code",
        "tax_name",
        "tax_rate",
        "taxable_amount",
        "tax_amount",
        "created_at",
    )
    list_filter = ("country_code", "tax_name", "created_at")
    search_fields = ("order__id", "country_code")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(VendorPayout)
class VendorPayoutAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "vendor",
        "gross_amount",
        "platform_commission",
        "net_payout_amount",
        "currency",
        "status",
        "payout_method",
        "processed_at",
    )
    list_filter = ("status", "currency", "payout_method", "created_at")
    search_fields = ("vendor__name", "reference_id")
    readonly_fields = ("id", "created_at", "updated_at")
    date_hierarchy = "created_at"