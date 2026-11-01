from decimal import Decimal

# Create your models here.
from django.conf import settings
from django.db import models


class CustomerGroup(models.Model):
    """فئات العملاء (تجزئة، جملة، VIP) لتطبيق سياسات الأسعار والخصومات"""
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم الفئة")
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.00'),
        verbose_name="نسبة الخصم الافتراضية للفئة %"
    )
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")

    class Meta:
        verbose_name = "فئة العميل"
        verbose_name_plural = "فئات العملاء"

    def __str__(self):
        return self.name


class Customer(models.Model):
    """ملف العميل التجاري والمؤسسي (مرتبط بنظام المستخدمين في Django)"""

    class CustomerType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', 'فرد (B2C)'
        COMPANY = 'COMPANY', 'شركة (B2B)'

    # ربط العميل بنظام المصادقة الافتراضي في Django
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='customer_profile', verbose_name="حساب المستخدم"
    )

    customer_type = models.CharField(
        max_length=20, choices=CustomerType.choices,
        default=CustomerType.INDIVIDUAL, verbose_name="نوع العميل"
    )

    # تفاصيل خاصة بالشركات (B2B)
    company_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="اسم الشركة")
    tax_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="الرقم الضريبي")

    # فئة العميل والسياسات المالية
    customer_group = models.ForeignKey(
        CustomerGroup, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='customers', verbose_name="فئة العميل"
    )
    credit_limit = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        verbose_name="الحد الائتماني المسموح"
    )

    phone_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم الهاتف")
    is_active = models.BooleanField(default=True, verbose_name="حساب نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")

    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"

    def __str__(self):
        if self.customer_type == self.CustomerType.COMPANY and self.company_name:
            return f"{self.company_name} ({self.user.email})"
        return f"{self.user.get_full_name() or self.user.email}"


class CustomerAddress(models.Model):
    """دفتر عناوين العميل (عناوين الشحن والفاتورة المتعددة)"""

    class AddressType(models.TextChoices):
        SHIPPING = 'SHIPPING', 'عنوان شحن'
        BILLING = 'BILLING', 'عنوان فاتورة'
        BOTH = 'BOTH', 'شحن وفاتورة معا'

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE,
        related_name='addresses', verbose_name="العميل"
    )
    address_type = models.CharField(
        max_length=20, choices=AddressType.choices,
        default=AddressType.BOTH, verbose_name="نوع العنوان"
    )

    recipient_name = models.CharField(max_length=255, verbose_name="اسم المستلم")
    phone_number = models.CharField(max_length=50, verbose_name="رقم هاتف المستلم")

    address_line1 = models.CharField(max_length=255, verbose_name="العنوان (السطر الأول)")
    address_line2 = models.CharField(max_length=255, blank=True, null=True, verbose_name="العنوان (السطر الثاني)")
    city = models.CharField(max_length=100, verbose_name="المدينة")
    state_province = models.CharField(max_length=100, blank=True, null=True, verbose_name="المنطقة / الولاية")
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="الرمز البريدي")
    country = models.CharField(max_length=100, verbose_name="الدولة")

    is_default = models.BooleanField(default=False, verbose_name="العنوان الافتراضي")

    class Meta:
        verbose_name = "عنوان العميل"
        verbose_name_plural = "عناوين العملاء"

    def __str__(self):
        return f"{self.recipient_name} - {self.city}, {self.country}"