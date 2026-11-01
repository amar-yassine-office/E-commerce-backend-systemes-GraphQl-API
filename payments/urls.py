from django.urls import path

from .views import nowpayments_ipn_webhook

urlpatterns = [
    path('webhook/nowpayments/', nowpayments_ipn_webhook, name='nowpayments_webhook'),
]