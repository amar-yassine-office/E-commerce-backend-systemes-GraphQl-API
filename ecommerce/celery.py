# ecommerce/ecommerce/celery.py

import os

from celery import Celery

# تعيين متغير البيئة الافتراضي لإعدادات ديجانجو لتطبيق ecommerce
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

app = Celery('ecommerce')

# قراءة الإعدادات من ملف settings.py الخاص بديجانجو على أن تبدأ بكلمة CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# البحث التلقائي عن ملفات tasks.py في جميع تطبيقات المشروع المسجلة
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
# this the     shedule


app.conf.beat_schedule = {
    'check-crypto-payments-every-5-minutes': {
        'task': 'accountante.tasks.check_pending_crypto_transactions',
        'schedule': 300.0,  # كل 5 دقائق
    },
}