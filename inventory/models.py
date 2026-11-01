# Create your models here.
from catalog.models import ProductVariant  # استيراد متغيرات المنتجات من تطبيق الكتالوج
from django.db import models


class Warehouse(models.Model):
    """المستودعات الرئيسية للشركات"""
    name = models.CharField(max_length=255, verbose_name="اسم المستودع")
    code = models.CharField(max_length=50, unique=True, verbose_name="كود المستودع")
    address = models.TextField(verbose_name="عنوان المستودع")
    is_active = models.BooleanField(default=True, verbose_name="نشط")

    def __str__(self):
        return f"{self.name} ({self.code})"


class StockLocation(models.Model):
    """مواقع التخزين الداخلية داخل المستودع (ممرات وأرفف)"""
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='locations',
                                  verbose_name="المستودع")
    name = models.CharField(max_length=100, verbose_name="اسم الموقع (مثل الرف A1)")
    code = models.CharField(max_length=50, unique=True, verbose_name="كود الموقع")

    def __str__(self):
        return f"{self.warehouse.code} -> {self.name}"


class InventoryStock(models.Model):
    """الرصيد الفعلي للمنتج في المستودع (يربط الكتالوج بالمستودع)"""
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stocks', verbose_name="المستودع")
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='stocks',
                                        verbose_name="متغير المنتج (SKU)")

    quantity_on_hand = models.IntegerField(default=0, verbose_name="الكمية الفعلية اليدوية")
    quantity_reserved = models.IntegerField(default=0, verbose_name="الكمية المحجوزة للطلبات")

    @property
    def available_quantity(self):
        """الكمية المتاحة للبيع الفعلي"""
        return self.quantity_on_hand - self.quantity_reserved

    class Meta:
        unique_together = ('warehouse', 'product_variant')
        verbose_name = "رصيد المخزون"
        verbose_name_plural = "أرصدة المخزون"

    def __str__(self):
        return f"SKU: {self.product_variant.sku} | Available: {self.available_quantity}"


class StockMovement(models.Model):
    """سجل حركات المخزون (دخول، خروج، تحويل)"""

    class MovementType(models.TextChoices):
        IN = 'IN', 'وارد (شراء/إضافة)'
        OUT = 'OUT', 'صادر (بيع/شحن)'
        TRANSFER = 'TRANSFER', 'تحويل بين المستودعات'

    product_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name='movements',
                                        verbose_name="متغير المنتج")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='movements',
                                  verbose_name="المستودع")

    movement_type = models.CharField(max_length=20, choices=MovementType.choices, verbose_name="نوع الحركة")
    quantity = models.IntegerField(verbose_name="الكمية")
    reference = models.CharField(max_length=100, blank=True, null=True,
                                 verbose_name="المرجع (رقم الطلب / فاتورة المورد)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ ووقت الحركة")

    def __str__(self):
        return f"{self.movement_type} - SKU: {self.product_variant.sku} (Qty: {self.quantity})"


class StockAdjustment(models.Model):
    """تسويات الجرد اليدوي ومعالجة العجز والتلف"""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'معلقة'
        APPROVED = 'APPROVED', 'معتمدة ومرحلة'

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='adjustments',
                                  verbose_name="المستودع")
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='adjustments',
                                        verbose_name="متغير المنتج")

    system_quantity = models.IntegerField(verbose_name="الكمية الدفترية في النظام")
    actual_quantity = models.IntegerField(verbose_name="الكمية الفعلية بعد الجرد")
    reason = models.TextField(verbose_name="سبب التسوية (تلف، عجز، سرقة)")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="الحالة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسوية")

    def __str__(self):
        return f"Adjustment for SKU: {self.product_variant.sku} - Status: {self.status}"


class ReorderRule(models.Model):
    """قواعد الحد الأدنى للمخزون وإعادة الطلب التلقائي"""
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='reorder_rules',
                                  verbose_name="المستودع")
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='reorder_rules',
                                        verbose_name="متغير المنتج")

    min_stock_level = models.IntegerField(verbose_name="حد التنبيه الأدنى")
    reorder_quantity = models.IntegerField(verbose_name="كمية إعادة الطلب المقترحة")

    class Meta:
        unique_together = ('warehouse', 'product_variant')

    def __str__(self):
        return f"Reorder Rule: {self.product_variant.sku} (Min: {self.min_stock_level})"