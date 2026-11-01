# Create your models here.
from decimal import Decimal

from catalog.models import Category, ProductVariant
from customers.models import Customer, CustomerGroup
from django.db import models
from orders.models import Order


class Coupon(models.Model):
    """كوبونات الخصم الترويجية"""

    class DiscountType(models.TextChoices):
        PERCENTAGE = 'PERCENTAGE', 'نسبة مئوية (%)'
        FIXED = 'FIXED', 'مبلغ ثابت'

    code = models.CharField(max_length=50, unique=True, verbose_name="كود الكوبون")
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices, verbose_name="نوع الخصم")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قيمة الخصم")

    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'),
                                           verbose_name="الحد الأدنى لقيمة الطلب")
    usage_limit = models.PositiveIntegerField(default=0, verbose_name="الحد الأقصى لعدد مرات الاستخدام (0 = غير محدود)")
    times_used = models.PositiveIntegerField(default=0, verbose_name="عدد مرات الاستخدام الفعلية")

    start_date = models.DateTimeField(verbose_name="تاريخ بدء الصلاحية")
    end_date = models.DateTimeField(verbose_name="تاريخ انتهاء الصلاحية")
    is_active = models.BooleanField(default=True, verbose_name="نشط")

    class Meta:
        verbose_name = "كوبون خصم"
        verbose_name_plural = "كوبونات الخصم"

    def __str__(self):
        return f"{self.code} ({self.discount_value})"


class Promotion(models.Model):
    """الحملات الترويجية التلقائية على المنتجات أو التصنيفات"""

    class DiscountType(models.TextChoices):
        PERCENTAGE = 'PERCENTAGE', 'نسبة مئوية (%)'
        FIXED = 'FIXED', 'مبلغ ثابت'

    name = models.CharField(max_length=150, verbose_name="اسم الحملة الترويجية")
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices, verbose_name="نوع الخصم")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قيمة الخصم")

    # العلاقات لاستهداف مجموعات معينة أو منتجات محددة
    customer_groups = models.ManyToManyField(CustomerGroup, blank=True, related_name='promotions',
                                             verbose_name="فئات العملاء المستهدفة")
    categories = models.ManyToManyField(Category, blank=True, related_name='promotions',
                                        verbose_name="التصنيفات المشمولة")
    product_variants = models.ManyToManyField(ProductVariant, blank=True, related_name='promotions',
                                              verbose_name="المنتجات المشمولة (SKUs)")

    start_date = models.DateTimeField(verbose_name="تاريخ البداية")
    end_date = models.DateTimeField(verbose_name="تاريخ النهاية")
    is_active = models.BooleanField(default=True, verbose_name="نشطة")

    class Meta:
        verbose_name = "حملة ترويجية"
        verbose_name_plural = "الحملات الترويجية"

    def __str__(self):
        return self.name


class GiftCard(models.Model):
    """بطاقات الهدايا والقسائم مسبقة الدفع"""
    code = models.CharField(max_length=100, unique=True, verbose_name="كود بطاقة الهدايا")
    initial_balance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الرصيد الأساسي")
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الرصيد الحالي المتبقي")

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='gift_cards',
                                 verbose_name="العميل المالك (اختياري)")

    expires_at = models.DateTimeField(verbose_name="تاريخ انتهاء الصلاحية")
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الاصدار")

    class Meta:
        verbose_name = "بطاقة هدايا"
        verbose_name_plural = "بطاقات الهدايا"

    def __str__(self):
        return f"GiftCard #{self.code} - Balance: {self.current_balance}"


class LoyaltyTransaction(models.Model):
    """سجل نقاط ولاء العملاء (كسب واستبدال النقاط)"""

    class TransactionType(models.TextChoices):
        EARNED = 'EARNED', 'نقاط مكتسبة من شراء'
        SPENT = 'SPENT', 'نقاط مستخدمة في خصم'
        EXPIRED = 'EXPIRED', 'نقاط منتهية الصلاحية'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loyalty_transactions',
                                 verbose_name="العميل")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='loyalty_transactions', verbose_name="الطلب المرتبط")

    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices, verbose_name="نوع الحركة")
    points = models.IntegerField(verbose_name="عدد النقاط (موجب أو سالب)")

    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الحركة")

    class Meta:
        verbose_name = "حركة نقاط ولاء"
        verbose_name_plural = "سجل ولاء العملاء"

    def __str__(self):
        return f"{self.customer} | {self.transaction_type}: {self.points} pts"