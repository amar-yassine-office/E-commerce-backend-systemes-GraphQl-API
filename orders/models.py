# Create your models here.
from decimal import Decimal

from catalog.models import ProductVariant
from django.db import models
from inventory.models import Warehouse


class Order(models.Model):
    """Master Order Header representing a customer purchase"""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'معلق (قيد الانتظار)'
        PROCESSING = 'PROCESSING', 'قيد المعالجة'
        COMPLETED = 'COMPLETED', 'مكتمل'
        CANCELLED = 'CANCELLED', 'ملغي'
        REFUNDED = 'REFUNDED', 'مسترجع بالكامل'

    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'غير مدفوع'
        PAID = 'PAID', 'مدفوع'
        FAILED = 'FAILED', 'فشل الدفع'
        REFUNDED = 'REFUNDED', 'تم الاسترداد'

    class FulfillmentStatus(models.TextChoices):
        UNFULFILLED = 'UNFULFILLED', 'لم يتم الشحن'
        PARTIAL = 'PARTIAL', 'شحن جزئي'
        FULFILLED = 'FULFILLED', 'تم الشحن بالكامل'

    # Customer Information
    customer_email = models.EmailField(verbose_name="بريد العميل")
    customer_name = models.CharField(max_length=255, verbose_name="اسم العميل")
    customer_phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم الهاتق")

    # Shipping Address
    shipping_address = models.TextField(verbose_name="عنوان الشحن")
    shipping_city = models.CharField(max_length=100, verbose_name="المدينة")
    shipping_country = models.CharField(max_length=100, verbose_name="الدولة")
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="الرمز البريدي")

    # Statuses
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="حالة الطلب")
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING,
                                      verbose_name="حالة الدفع")
    fulfillment_status = models.CharField(max_length=20, choices=FulfillmentStatus.choices,
                                          default=FulfillmentStatus.UNFULFILLED, verbose_name="حالة الشحن")

    # Financial Totals
    currency = models.CharField(max_length=10, default='USD', verbose_name="العملة")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="المجموع الفرعي")
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'),
                                    verbose_name="إجمالي الضريبة")
    shipping_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'),
                                         verbose_name="تكلفة الشحن")
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'),
                                         verbose_name="إجمالي الخصم")
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="الإجمالي النهائي")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ إنشاء الطلب")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    class Meta:
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name} ({self.grand_total} {self.currency})"


class OrderItem(models.Model):
    """Individual line items within an order (Linked to Catalog Variant)"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="الطلب")

    # Relationship to Catalog
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name='order_items',
                                        verbose_name="متغير المنتج (SKU)")

    # Snapshot data to preserve historical records even if catalog changes later
    product_name = models.CharField(max_length=255, verbose_name="اسم المنتج أثناء الشراء")
    sku = models.CharField(max_length=100, verbose_name="كود SKU")

    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="سعر الوحدة")
    quantity = models.PositiveIntegerField(default=1, verbose_name="الكمية المطلوبة")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="الإجمالي للبند")

    class Meta:
        verbose_name = "بند الطلب"
        verbose_name_plural = "بنود الطلبات"

    def __str__(self):
        return f"Order #{self.order.id} | {self.sku} (Qty: {self.quantity})"


class OrderFulfillment(models.Model):
    """Shipment dispatch record connected to the Warehouse inventory"""

    class Status(models.TextChoices):
        PROCESSING = 'PROCESSING', 'قيد التجهيز'
        SHIPPED = 'SHIPPED', 'تم الشحن'
        DELIVERED = 'DELIVERED', 'تم التوصيل'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='fulfillments', verbose_name="الطلب")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='fulfillments',
                                  verbose_name="مستودع الشحن")

    tracking_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="رقم تتبع الشحنة")
    carrier_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="شركة الشحن")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROCESSING,
                              verbose_name="حالة الشحنة")

    shipped_at = models.DateTimeField(blank=True, null=True, verbose_name="تاريخ الشحن الفعلي")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "شحنة الطلب"
        verbose_name_plural = "شحنات الطلبات"

    def __str__(self):
        return f"Fulfillment #{self.id} for Order #{self.order.id}"


class OrderFulfillmentItem(models.Model):
    """Line items included in a specific shipment (Supports partial shipments)"""
    fulfillment = models.ForeignKey(OrderFulfillment, on_delete=models.CASCADE, related_name='items',
                                    verbose_name="الشحنة")
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='fulfillment_items',
                                   verbose_name="بند الطلب")
    quantity = models.PositiveIntegerField(verbose_name="الكمية المشحونة في هذه الدفعة")

    class Meta:
        verbose_name = "بند الشحنة"
        verbose_name_plural = "بنود الشحنات"

    def __str__(self):
        return f"Fulfillment Item: Qty {self.quantity} for Order Item #{self.order_item.id}"


class ReturnOrder(models.Model):
    """Return Merchandise Authorization (RMA) for customer refunds or exchanges"""

    class Status(models.TextChoices):
        REQUESTED = 'REQUESTED', 'مطلب إرجاع جديد'
        APPROVED = 'APPROVED', 'تمت الموافقة'
        REJECTED = 'REJECTED', 'مرفوض'
        RECEIVED = 'RECEIVED', 'تم استلام البضاعة في المستودع'
        REFUNDED = 'REFUNDED', 'تم رد المبلغ المالي'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns', verbose_name="الطلب الأصلي")
    reason = models.TextField(verbose_name="سبب الاسترجاع")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED,
                              verbose_name="حالة الاسترجاع")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")

    class Meta:
        verbose_name = "طلب إرجاع (RMA)"
        verbose_name_plural = "طلبات الإرجاع"

    def __str__(self):
        return f"Return #{self.id} for Order #{self.order.id}"


class ReturnItem(models.Model):
    """Specific items and quantities being returned"""
    return_order = models.ForeignKey(ReturnOrder, on_delete=models.CASCADE, related_name='items',
                                     verbose_name="طلب الإرجاع")
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='return_items',
                                   verbose_name="بند الطلب الأصلي")
    quantity = models.PositiveIntegerField(verbose_name="الكمية المرتجعة")
    condition = models.CharField(max_length=100, blank=True, null=True, verbose_name="حالة المنتج عند الاستلام")

    class Meta:
        verbose_name = "بند الاسترجاع"
        verbose_name_plural = "بنود الاسترجاع"

    def __str__(self):
        return f"Return Item: Qty {self.quantity} from Order Item #{self.order_item.id}"