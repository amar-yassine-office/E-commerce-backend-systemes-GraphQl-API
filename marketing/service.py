# marketing/services.py

# استيراد مهام Celery الخاصة بالتسويق
from .tasks import update_marketing_campaigns_status_task, award_loyalty_points_task
from .models import Coupon, Promotion, GiftCard, LoyaltyTransaction


class MarketingManagementService:

    @staticmethod
    def process_order_loyalty_points(customer_id, order_id, order_total):
        """
        خدمة لحساب ومنح نقاط الولاء للعميل بناءً على قيمة الطلب وتشغيل المهمة في الخلفية
        """
        # مثال قاعدة الاحتساب: كل 10 وحدات نقدية تمنح نقطة ولاء واحدة
        earned_points = int(order_total / 10)

        if earned_points > 0:
            # تشغيل مهمة Celery لمنح النقاط في الخلفية
            award_loyalty_points_task.delay(
                customer_id=customer_id,
                order_id=order_id,
                points_amount=earned_points,
                notes=f"نقاط ولاء مكتسبة من الطلب رقم #{order_id}"
            )

        return earned_points

    @staticmethod
    def trigger_campaigns_status_check():
        """
        خدمة لتشغيل مهمة تحديث حالة الحملات والكوبونات يدوياً
        """
        update_marketing_campaigns_status_task.delay()
        return "Campaigns status check task triggered successfully."