# Create your models here.
from decimal import Decimal

from catalog.models import ProductVariant
from django.db import models
from inventory.models import Warehouse


class Vendor(models.Model):
    """ملف المورد الأساسي (شركات التوريد والمصانع)"""
    name = models.CharField(max_length=255, verbose_name="اسم المورد / الشركة")
    code = models.CharField(max_length=50, unique=True, verbose_name="كود المورد التعريفي")
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name="اسم المسؤول للمراسلة")
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    phone = models.CharField(max_length=50, verbose_name="رقم الهاتف")
    address = models.TextField(verbose_name="عنوان المورد")
    tax_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="الرقم الضريبي للمورد")

    currency = models.CharField(max_length=10, default='USD', verbose_name="العملة المعتمدة")
    payment_terms = models.CharField(max_length=100, default='Net 30', verbose_name="شروط السداد (مثل Net 30)")

    is_active = models.BooleanField(default=True, verbose_name="مورد نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    class Meta:
        verbose_name = "مورد"
        verbose_name_plural = "الموردون"

    def __str__(self):
        return f"{self.name} ({self.code})"


class PurchaseOrder(models.Model):
    """أوامر الشراء المرسلة إلى الموردين لتجديد المخزون"""

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'مسودة'
        SENT = 'SENT', 'تم الإرسال للمورد'
        CONFIRMED = 'CONFIRMED', 'مؤكد'
        RECEIVED = 'RECEIVED', 'تم الاستلام بالمستودع'
        CANCELLED = 'CANCELLED', 'ملغي'

    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='purchase_orders', verbose_name="المورد")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='purchase_orders',
                                  verbose_name="المستودع المستلم")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT,
                              verbose_name="حالة أمر الشراء")

    order_date = models.DateField(verbose_name="تاريخ أمر الشراء")
    expected_delivery_date = models.DateField(blank=True, null=True, verbose_name="تاريخ التوريد المتوقع")

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="المجموع الفرعي")
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'),
                                    verbose_name="إجمالي الضريبة")
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="الإجمالي النهائي")

    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات وشروط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "أمر شراء"
        verbose_name_plural = "أوامر الشراء"

    def __str__(self):
        return f"PO #{self.id} - {self.vendor.name} ({self.grand_total})"


class PurchaseOrderItem(models.Model):
    """بنود المنتجات المطلوبة في أمر الشراء"""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items',
                                       verbose_name="أمر الشراء")
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name='purchase_items',
                                        verbose_name="متغير المنتج (SKU)")

    quantity_ordered = models.PositiveIntegerField(verbose_name="الكمية المطلوبة")
    quantity_received = models.PositiveIntegerField(default=0, verbose_name="الكمية المستلامة فعلياً")

    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="سعر الشراء للوحدة")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="الإجمالي للبند")

    class Meta:
        verbose_name = "بند أمر الشراء"
        verbose_name_plural = "بنود أوامر الشراء"

    def __str__(self):
        return f"PO #{self.purchase_order.id} | SKU: {self.product_variant.sku} (Qty: {self.quantity_ordered})"


class VendorBill(models.Model):
    """فواتير الموردين المالية (الذمم الدائنة - Accounts Payable)"""

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'مسودة'
        POSTED = 'POSTED', 'مرحلة (معتمدة)'
        PAID = 'PAID', 'مدفوعة بالكامل'
        OVERDUE = 'OVERDUE', 'متأخرة السداد'

    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='bills', verbose_name="المورد")
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='bills', verbose_name="أمر الشراء المرتبط")

    bill_number = models.CharField(max_length=100, unique=True, verbose_name="رقم الفاتورة عند المورد")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name="حالة الفاتورة")

    bill_date = models.DateField(verbose_name="تاريخ الفاتورة")
    due_date = models.DateField(verbose_name="تاريخ الاستحقاق")

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="المجموع الفرعي")
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'),
                                    verbose_name="إجمالي الضريبة")
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="الإجمالي الواجب سداده")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")

    class Meta:
        verbose_name = "فاتورة مورد"
        verbose_name_plural = "فواتير الموردين (الذمم الدائنة)"

    def __str__(self):
        return f"Bill #{self.bill_number} - {self.vendor.name} ({self.grand_total})"