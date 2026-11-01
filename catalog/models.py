# Create your models here.

from django.db import models


class Category(models.Model):
    """تصنيفات المنتجات"""
    name = models.CharField(max_length=255, verbose_name="اسم التصنيف")
    slug = models.SlugField(unique=True, max_length=255, verbose_name="الرابط المختصر (Slug)")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories',
                               verbose_name="التصنيف الرئيسي")
    is_active = models.BooleanField(default=True, verbose_name="نشط")

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"

    def __str__(self):
        return self.name


class Brand(models.Model):
    """العلامات التجارية للمنتجات"""
    name = models.CharField(max_length=255, unique=True, verbose_name="اسم العلامة التجارية")
    slug = models.SlugField(unique=True, max_length=255, verbose_name="الرابط المختصر")
    is_active = models.BooleanField(default=True, verbose_name="نشطة")

    class Meta:
        verbose_name = "علامة تجارية"
        verbose_name_plural = "العلامات التجارية"

    def __str__(self):
        return self.name


class Product(models.Model):
    """المنتج الأساسي"""
    name = models.CharField(max_length=255, verbose_name="اسم المنتج")
    slug = models.SlugField(unique=True, max_length=255, verbose_name="الرابط المختصر")
    description = models.TextField(verbose_name="وصف المنتج")

    # العلاقات الأساسية
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name="التصنيف")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products',
                              verbose_name="العلامة التجارية")

    is_active = models.BooleanField(default=True, verbose_name="نشط للبيع")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"

    def __str__(self):
        return self.name


class Attribute(models.Model):
    """خصائص المنتجات (مثل: اللون، المقاس)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم الخاصية")

    class Meta:
        verbose_name = "خاصية منتج"
        verbose_name_plural = "خصائص المنتجات"

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    """قيم الخصائص (مثل: أحمر، XL)"""
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values', verbose_name="الخاصية")
    value = models.CharField(max_length=100, verbose_name="القيمة")

    class Meta:
        verbose_name = "قيمة الخاصية"
        verbose_name_plural = "قيم الخصائص"

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductVariant(models.Model):
    """متغيرات المنتج الفردية (SKU)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants',
                                verbose_name="المنتج الأساسي")
    sku = models.CharField(max_length=100, unique=True, verbose_name="كود المنتج الفريد (SKU)")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="سعر البيع")
    compare_at_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                           verbose_name="السعر قبل الخصم")
    attribute_values = models.ManyToManyField(AttributeValue, related_name='variants', verbose_name="قيم الخصائص")
    is_active = models.BooleanField(default=True, verbose_name="متوفر للبيع")

    class Meta:
        verbose_name = "متغير المنتج (SKU)"
        verbose_name_plural = "متغيرات المنتجات (SKUs)"

    def __str__(self):
        return f"{self.product.name} - SKU: {self.sku}"


class ProductImage(models.Model):
    """صور المنتجات"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="المنتج")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True, related_name='images',
                                verbose_name="متغير المنتج المخصص")
    image = models.ImageField(upload_to='products/', verbose_name="ملف الصورة")
    is_feature = models.BooleanField(default=False, verbose_name="صورة رئيسية")

    class Meta:
        verbose_name = "صورة المنتج"
        verbose_name_plural = "صور المنتجات"

    def __str__(self):
        return f"Image for {self.product.name}"