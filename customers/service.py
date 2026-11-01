# marketing/services.py

# استيراد مهام Celery الخاصة بالعملاء والتسويق
from .models import Customer, CustomerGroup
from .tasks import send_welcome_notification_task


class CustomerManagementService:

    @staticmethod
    def register_new_customer(user, customer_type, phone_number=None, company_name=None, tax_id=None,
                              customer_group_id=None):
        """
        خدمة لإنشاء ملف عميل جديد وتشغيل مهمة الترحيب في الخلفية
        """
        group = None
        if customer_group_id:
            group = CustomerGroup.objects.filter(id=customer_group_id).first()

        # إنشاء ملف العميل
        customer = Customer.objects.create(
            user=user,
            customer_type=customer_type,
            phone_number=phone_number,
            company_name=company_name,
            tax_id=tax_id,
            customer_group=group
        )

        # تشغيل مهمة الترحيب في الخلفية عبر Celery دون إبطاء استجابة التسجيل
        send_welcome_notification_task.delay(customer.id)

        return customer

    @staticmethod
    def update_group_discount(group_id, new_discount_percentage):
        """
        خدمة لتحديث نسبة الخصم لفئة العملاء وتشغيل مهمة تحديث الكاش في الخلفية
        """
        group = CustomerGroup.objects.get(id=group_id)
        group.discount_percentage = new_discount_percentage
        group.save()

        # استدعاء مهمة Celery لتحديث الكاش المرتبط بالفئة
        update_group_cache_task.delay(group.id)

        return group