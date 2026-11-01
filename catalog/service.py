# catalog/services.py

# استيراد مهام Celery الخاصة بالكاتالوج
from .models import ProductVariant
from .tasks import invalidate_catalog_cache_task, optimize_product_image_task


class CatalogManagementService:

    @staticmethod
    def handle_new_product_image_upload(image_instance_id):
        """
        خدمة تُستدعى بعد رفع صورة المنتج لتشغيل معالجتها في الخلفية
        """
        # تشغيل مهمة معالجة وضغط الصورة في الخلفية فوراً دون إبطاء رفع الملف
        optimize_product_image_task.delay(image_instance_id)

    @staticmethod
    def update_variant_pricing(variant_id, new_price, new_compare_price=None):
        """
        خدمة لتحديث سعر متغير المنتج ومسح الكاش المرتبط به تلقائياً
        """
        variant = ProductVariant.objects.get(id=variant_id)
        variant.price = new_price
        if new_compare_price is not None:
            variant.compare_at_price = new_compare_price
        variant.save()

        # استدعاء مهمة Celery لمسح الكاش وتحديث الواجهة الخلفية للبحث في الخلفية
        invalidate_catalog_cache_task.delay(variant.product.id)

        return variant