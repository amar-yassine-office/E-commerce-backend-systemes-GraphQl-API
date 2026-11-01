from decimal import Decimal
import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseAccountingModel(models.Model):
    """Abstract base model adding UUID and timestamps."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Currency(BaseAccountingModel):
    """ISO 4217 Currency table for multi-currency handling."""

    code = models.CharField(
        max_length=3, unique=True, help_text=_("ISO code (e.g., USD, EUR)")
    )
    symbol = models.CharField(max_length=10, default="$")
    name = models.CharField(max_length=50)
    exchange_rate_to_base = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        default=Decimal("1.00000000"),
        help_text=_("Exchange rate relative to base system currency"),
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Currencies"
        ordering = ["code"]

    def __str__(self):
        return self.code


class ChartOfAccount(BaseAccountingModel):
    """International Chart of Accounts supporting multi-currency ledgers."""

    class AccountType(models.TextChoices):
        ASSET = "asset", _("Asset")
        LIABILITY = "liability", _("Liability")
        EQUITY = "equity", _("Equity")
        REVENUE = "revenue", _("Revenue")
        EXPENSE = "expense", _("Expense")

    class SubType(models.TextChoices):
        CASH = "cash", _("Cash & Bank")
        CRYPTO_WALLET = "crypto_wallet", _("Crypto Wallet")
        ACCOUNTS_RECEIVABLE = "receivable", _("Accounts Receivable")
        ACCOUNTS_PAYABLE = "payable", _("Accounts Payable")
        COGS = "cogs", _("Cost of Goods Sold")
        SHIPPING_EXPENSE = "shipping_expense", _("Shipping Expense")
        MARKETING_EXPENSE = "marketing_expense", _("Marketing Expense")
        SALES_REVENUE = "sales_revenue", _("Sales Revenue")
        TAX_PAYABLE = "tax_payable", _("Tax/VAT Payable")
        VENDOR_PAYABLE = "vendor_payable", _("Vendor Payable")

    code = models.CharField(
        max_length=20, unique=True, db_index=True, help_text=_("e.g. 1010, 4000")
    )
    name = models.CharField(max_length=100)
    account_type = models.CharField(
        max_length=20, choices=AccountType.choices, db_index=True
    )
    sub_type = models.CharField(
        max_length=30, choices=SubType.choices, blank=True, null=True
    )
    currency = models.ForeignKey(
        Currency, on_delete=models.PROTECT, related_name="accounts"
    )
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"[{self.code}] {self.name} ({self.currency.code})"


class JournalEntry(BaseAccountingModel):
    """Balanced double-entry journal transaction linking core operational modules."""

    class SourceModule(models.TextChoices):
        ORDER = "order", _("Order Management")
        CRYPTO_PAYMENT = "crypto_payment", _("NOWPayments Gateway")
        FIAT_PAYMENT = "fiat_payment", _("Fiat Payment Gateway")
        SHIPPING = "shipping", _("Shipping Logistics")
        MARKETING = "marketing", _("Marketing Campaign")
        VENDOR = "vendor", _("Vendor Payout")
        TAX = "tax", _("Tax Settlement")
        MANUAL = "manual", _("Manual Adjustment")

    entry_number = models.CharField(
        max_length=64, unique=True, db_index=True, help_text=_("Auto-generated reference string")
    )
    date = models.DateField(db_index=True)
    description = models.TextField()
    source_module = models.CharField(
        max_length=30, choices=SourceModule.choices, default=SourceModule.MANUAL, db_index=True
    )
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)

    # Cross-module references
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accounting_entries",
    )
    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accounting_entries",
    )

    is_posted = models.BooleanField(
        default=False, help_text=_("Posted entries are locked against modification")
    )

    class Meta:
        verbose_name_plural = "Journal Entries"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"JE {self.entry_number} ({self.date})"

    def clean(self):
        super().clean()
        if self.is_posted and self.pk:
            debits = (
                    self.items.aggregate(models.Sum("debit"))["debit__sum"]
                    or Decimal("0.00")
            )
            credits = (
                    self.items.aggregate(models.Sum("credit"))["credit__sum"]
                    or Decimal("0.00")
            )
            if debits != credits:
                raise ValidationError(
                    _(
                        f"Unbalanced Journal Entry: Debits ({debits}) must equal Credits ({credits})."
                    )
                )


class JournalItem(BaseAccountingModel):
    """Line items for debit and credit entries."""

    journal_entry = models.ForeignKey(
        JournalEntry, on_delete=models.CASCADE, related_name="items"
    )
    account = models.ForeignKey(
        ChartOfAccount, on_delete=models.PROTECT, related_name="journal_items"
    )
    debit = models.DecimalField(
        max_digits=18, decimal_places=4, default=Decimal("0.0000")
    )
    credit = models.DecimalField(
        max_digits=18, decimal_places=4, default=Decimal("0.0000")
    )
    memo = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        val = f"Dr {self.debit}" if self.debit > 0 else f"Cr {self.credit}"
        return f"{self.account.name}: {val}"


class CryptoTransaction(BaseAccountingModel):
    """NOWPayments crypto transaction ledger entry."""

    class PaymentStatus(models.TextChoices):
        WAITING = "waiting", _("Waiting")
        CONFIRMING = "confirming", _("Confirming")
        CONFIRMED = "confirmed", _("Confirmed")
        SENDING = "sending", _("Sending")
        PARTIALLY_PAID = "partially_paid", _("Partially Paid")
        FINISHED = "finished", _("Finished")
        FAILED = "failed", _("Failed")
        REFUNDED = "refunded", _("Refunded")
        EXPIRED = "expired", _("Expired")

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="accountante_crypto_transactions",  # اسم فريد لتجنب التضارب
    )
    nowpayments_id = models.CharField(
        max_length=100, unique=True, db_index=True
    )
    invoice_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(
        max_length=25, choices=PaymentStatus.choices, default=PaymentStatus.WAITING, db_index=True
    )
    pay_address = models.CharField(max_length=255)

    # Fiat base values
    price_amount = models.DecimalField(max_digits=14, decimal_places=2)
    price_currency = models.CharField(max_length=10, default="USD")

    # Crypto target values
    pay_amount = models.DecimalField(max_digits=24, decimal_places=12)
    pay_currency = models.CharField(max_length=15)  # BTC, ETH, USDT, etc.
    actually_paid = models.DecimalField(
        max_digits=24, decimal_places=12, default=Decimal("0.000000000000")
    )

    outcome_amount = models.DecimalField(
        max_digits=24, decimal_places=12, null=True, blank=True
    )
    outcome_currency = models.CharField(max_length=15, null=True, blank=True)

    network_fee = models.DecimalField(
        max_digits=24, decimal_places=12, default=Decimal("0.000000000000")
    )
    service_fee = models.DecimalField(
        max_digits=24, decimal_places=12, default=Decimal("0.000000000000")
    )

    journal_entry = models.OneToOneField(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crypto_transaction",
    )

    def __str__(self):
        return f"NOWPayments #{self.nowpayments_id} [{self.payment_status}]"


class TaxRecord(BaseAccountingModel):
    """International VAT/Sales Tax records per transaction jurisdiction."""

    order = models.ForeignKey(
        "orders.Order", on_delete=models.PROTECT, related_name="tax_records"
    )
    country_code = models.CharField(
        max_length=2, help_text=_("ISO 3166-1 alpha-2 country code")
    )
    state_or_province = models.CharField(max_length=50, blank=True, null=True)
    tax_name = models.CharField(
        max_length=50, help_text=_("VAT, GST, State Sales Tax")
    )
    tax_rate = models.DecimalField(
        max_digits=6, decimal_places=4, help_text=_("Percentage rate e.g. 0.2000 for 20%")
    )
    taxable_amount = models.DecimalField(max_digits=14, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2)

    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tax_records",
    )

    def __str__(self):
        return f"{self.country_code} {self.tax_name} ({self.tax_amount})"


class VendorPayout(BaseAccountingModel):
    """Multi-vendor platform payout processing and commission breakdown."""

    class PayoutStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")
        COMPLETED = "completed", _("Completed")
        FAILED = "failed", _("Failed")

    vendor = models.ForeignKey(
        "vendors.Vendor", on_delete=models.PROTECT, related_name="payouts"
    )
    gross_amount = models.DecimalField(max_digits=14, decimal_places=2)
    platform_commission = models.DecimalField(max_digits=14, decimal_places=2)
    net_payout_amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)

    status = models.CharField(
        max_length=20, choices=PayoutStatus.choices, default=PayoutStatus.PENDING, db_index=True
    )
    payout_method = models.CharField(
        max_length=50, help_text=_("Crypto Wallet, Bank Wire, Stripe Connect")
    )
    reference_id = models.CharField(max_length=255, blank=True, null=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    journal_entry = models.OneToOneField(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vendor_payout",
    )

    def __str__(self):
        return f"Payout {self.net_payout_amount} {self.currency.code} to Vendor: {self.vendor}"