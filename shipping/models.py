# Create your models here.
from decimal import Decimal

from django.db import models


class ShippingZone(models.Model):
    """مناطق الشحن الجغرافية (مثل: دول الخليج، الاتحاد الأوروبي، محلي)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم منطقة الشحن")
    countries = models.TextField(help_text="أدخل رموز الدول يفصل بينها فاصلة (مثال: SA, AE, KW)",
                                 verbose_name="الدول المشمولة")
    is_active = models.BooleanField(default=True, verbose_name="نشطة")

    class Meta:
        verbose_name = "منطقة شحن"
        verbose_name_plural = "مناطق الشحن"

    def __str__(self):
        return self.name


class ShippingCarrier(models.Model):
    """شركات الشحن والخدمات اللوجستية (مثل DHL, Aramex, SMSA)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم شركة الشحن")
    code = models.CharField(max_length=50, unique=True, verbose_name="الكود التعريفي للشركة")
    tracking_url_template = models.URLField(blank=True, null=True,
                                            help_text="استخدم {tracking_code} كمتغير لرابط التتبع",
                                            verbose_name="رابط التتبع")
    is_active = models.BooleanField(default=True, verbose_name="نشطة")

    class Meta:
        verbose_name = "شركة شحن"
        verbose_name_plural = "شركات الشحن"

    def __str__(self):
        return self.name


class ShippingMethod(models.Model):
    """طرق أو مستويات الشحن (مثل: شحن سريع، شحن اقتصادي)"""
    carrier = models.ForeignKey(ShippingCarrier, on_delete=models.CASCADE, related_name='methods',
                                verbose_name="شركة الشحن")
    name = models.CharField(max_length=100, verbose_name="اسم طريقة الشحن")
    description = models.TextField(blank=True, null=True, verbose_name="وصف الخدمة")
    is_active = models.BooleanField(default=True, verbose_name="متاحة للعملاء")

    class Meta:
        verbose_name = "طريقة شحن"
        verbose_name_plural = "طرق الشحن"

    def __str__(self):
        return f"{self.carrier.name} - {self.name}"


class ShippingRate(models.Model):
    """جدول أسعار الشحن بناءً على المنطقة، الوزن، أو قيمة الطلب"""

    class PricingType(models.TextChoices):
        FLAT_RATE = 'FLAT', 'سعر ثابت'
        WEIGHT_BASED = 'WEIGHT', 'حسب الوزن'
        PRICE_BASED = 'PRICE', 'حسب قيمة الطلب'

    method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE, related_name='rates',
                               verbose_name="طريقة الشحن")
    zone = models.ForeignKey(ShippingZone, on_delete=models.CASCADE, related_name='rates', verbose_name="منطقة الشحن")

    pricing_type = models.CharField(max_length=20, choices=PricingType.choices, default=PricingType.FLAT_RATE,
                                    verbose_name="نوع التسعير")

    base_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'),
                                    verbose_name="التكلفة الأساسية")

    # حدود الوزن أو القيمة لتطبيق السعر
    min_weight = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'),
                                     verbose_name="الحد الأدنى للوزن (كجم)")
    max_weight = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('9999.00'),
                                     verbose_name="الحد الأقصى للوزن (كجم)")

    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'),
                                           verbose_name="الحد الأدنى لقيمة الطلب")
    max_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('999999.00'),
                                           verbose_name="الحد الأقصى لقيمة الطلب")

    class Meta:
        verbose_name = "سعر شحن"
        verbose_name_plural = "أسعار الشحن"

    def __str__(self):
        return f"{self.method} | Zone: {self.zone.name} | Cost: {self.base_cost}"