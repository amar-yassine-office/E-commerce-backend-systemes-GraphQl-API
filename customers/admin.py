from django.contrib import admin

# Register your models here.
from .models import Customer, CustomerAddress, CustomerGroup


@admin.register(CustomerGroup)
class CustomerGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_percentage')
    search_fields = ('name',)

class CustomerAddressInline(admin.TabularInline):
    model = CustomerAddress
    extra = 1

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'customer_type', 'company_name', 'customer_group', 'credit_limit', 'is_active', 'created_at')
    list_filter = ('customer_type', 'is_active', 'customer_group')
    search_fields = ('user__email', 'user__first_name', 'company_name', 'tax_id')
    inlines = [CustomerAddressInline]

@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'recipient_name', 'city', 'country', 'address_type', 'is_default')
    list_filter = ('address_type', 'country', 'is_default')
    search_fields = ('recipient_name', 'city', 'customer__user__email')