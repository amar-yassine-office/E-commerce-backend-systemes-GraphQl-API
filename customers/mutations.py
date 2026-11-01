import strawberry
from customers.types import (
    CustomerType, CustomerGroupType, CustomerAddressType,
    CustomerInput, CustomerGroupInput, CustomerAddressInput
)
from customers.services import CustomerService


@strawberry.type
class Mutation:

    @strawberry.mutation
    def create_customer_group(self, input: CustomerGroupInput) -> CustomerGroupType:
        """إنشاء فئة عملاء جديدة"""
        return CustomerService.create_group(
            name=input.name,
            discount_percentage=input.discount_percentage,
            description=input.description
        )

    @strawberry.mutation
    def create_customer(self, user_id: int, input: CustomerInput) -> CustomerType:
        """ربط مستخدم بملف عميل جديد"""
        data = {
            "customer_type": input.customer_type,
            "company_name": input.company_name,
            "tax_id": input.tax_id,
            "customer_group_id": input.customer_group_id,
            "credit_limit": input.credit_limit,
            "phone_number": input.phone_number,
            "is_active": input.is_active,
        }
        return CustomerService.create_customer(user_id=user_id, data=data)

    @strawberry.mutation
    def create_customer_address(self, input: CustomerAddressInput) -> CustomerAddressType:
        """إضافة عنوان جديد لعميل"""
        data = {
            "address_type": input.address_type,
            "recipient_name": input.recipient_name,
            "phone_number": input.phone_number,
            "address_line1": input.address_line1,
            "address_line2": input.address_line2,
            "city": input.city,
            "state_province": input.state_province,
            "postal_code": input.postal_code,
            "country": input.country,
            "is_default": input.is_default,
        }
        return CustomerService.add_address(customer_id=input.customer_id, data=data)