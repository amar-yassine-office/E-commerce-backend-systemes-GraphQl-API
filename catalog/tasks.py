from celery import shared_task
from django.core.cache import cache
from .models import ProductImage, ProductVariant


@shared_task(bind=True, max_retries=3)
def optimize_product_image_task(self, image_id):
    """
    مهمة خلفية لمعالجة وضغط صور المنتجات وتوليد النسخ المصغرة
    """
    try:
        product_image = ProductImage.objects.get(id=image_id)
        # هنا يتم وضع كود معالجة الصورة (مثل استخدام مكتبة Pillow لضغط الصورة أو تغيير قياساتها)
        # مثال محاكاة:
        image_path = product_image.image.path
        # ... كود معالجة وتعديل الصورة ...

        return f"Successfully optimized image for product: {product_image.product.name}"

    except ProductImage.DoesNotExist:
        return "Image not found."
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)


@shared_task(bind=True)
def invalidate_catalog_cache_task(self, product_id):
    """
    مهمة خلفية لمسح الكاش الخاص بالمنتج وتحديث بيانات البحث عند تعديل الأسعار أو الخصائص
    """
    try:
        # مسح الـ Cache الخاص بالمنتج لضمان ظهور السعر الجديد فوراً للعملاء
        cache_key = f"product_detail_{product_id}"
        cache.delete(cache_key)
        cache.delete("home_featured_products")  # مسح كاش الصفحة الرئيسية أيضاً

        return f"Successfully invalidated cache for Product ID: {product_id}"

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)d_t