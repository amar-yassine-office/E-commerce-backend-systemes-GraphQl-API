import strawberry
from decimal import Decimal
from typing import List, Optional

# استيراد النماذج من تطبيق customers
from customers.models import CustomerGroup, Customer, CustomerAddress


@strawberry.django.type(CustomerGroup)
class CustomerGroupType:
    id: strawberry.ID
    name: str
    discount_percentage: Decimal
    description: Optional[str]


@strawberry.django.type(CustomerAddress)
class CustomerAddressType:
    id: strawberry.ID
    address_type: str
    recipient_name: str
    phone_number: str
    address_line1: str
    address_line2: Optional[str]
    city: str
    state_province: Optional[str]
    postal_code: Optional[str]
    country: str
    is_default: bool


@strawberry.django.type(Customer)
class CustomerType:
    id: strawberry.ID
    customer_type: str
    company_name: Optional[str]
    tax_id: Optional[str]
    credit_limit: Decimal
    phone_number: Optional[str]
    is_active: bool
    created_at: str

    # العلاقات
    customer_group: Optional[CustomerGroupType]
    addresses: List[CustomerAddressType]


# --- مدخلات البيانات (Input Types) للـ Mutations ---

@strawberry.input
class CustomerGroupInput:
    name: str
    discount_percentage: Optional[Decimal] = Decimal('0.00')
    description: Optional[str] = None


@strawberry.input
class CustomerInput:
    customer_type: str = "INDIVIDUAL"
    company_name: Optional[str] = None
    tax_id: Optional[str] = None
    customer_group_id: Optional[int] = None
    credit_limit: Optional[Decimal] = Decimal('0.00')
    phone_number: Optional[str] = None
    is_active: Optional[bool] = True


@strawberry.input
class CustomerAddressInput:
    customer_id: int
    address_type: str = "BOTH"
    recipient_name: str
    phone_number: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: str
    is_default: Optional[bool] = False