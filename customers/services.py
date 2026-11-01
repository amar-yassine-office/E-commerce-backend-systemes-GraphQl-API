from decimal import Decimal
from typing import List, Optional
from django.contrib.auth import get_user_model
from customers.models import CustomerGroup, Customer, CustomerAddress

User = get_user_model()


class CustomerService:

    # --- فئات العملاء (Customer Groups) ---
    @staticmethod
    def get_all_groups() -> List[CustomerGroup]:
        return CustomerGroup.objects.all()

    @staticmethod
    def create_group(name: str, discount_percentage: Decimal, description: Optional[str]) -> CustomerGroup:
        return CustomerGroup.objects.create(
            name=name,
            discount_percentage=discount_percentage,
            description=description
        )

    # --- العملاء (Customers) ---
    @staticmethod
    def get_all_customers() -> List[Customer]:
        return Customer.objects.select_related('user', 'customer_group').prefetch_related('addresses').all()

    @staticmethod
    def get_customer_by_id(customer_id: int) -> Optional[Customer]:
        try:
            return Customer.objects.select_related('user', 'customer_group').prefetch_related('addresses').get(
                pk=customer_id)
        except Customer.DoesNotExist:
            return None

    @staticmethod
    def create_customer(user_id: int, data: dict) -> Customer:
        user = User.objects.get(pk=user_id)
        group_id = data.pop('customer_group_id', None)
        group = CustomerGroup.objects.filter(pk=group_id).first() if group_id else None

        customer = Customer.objects.create(
            user=user,
            customer_group=group,
            **data
        )
        return customer

    # --- العناوين (Customer Addresses) ---
    @staticmethod
    def add_address(customer_id: int, data: dict) -> CustomerAddress:
        customer = Customer.objects.get(pk=customer_id)

        if data.get('is_default', False):
            CustomerAddress.objects.filter(customer=customer).update(is_default=False)

        address = CustomerAddress.objects.create(customer=customer, **data)
        return address