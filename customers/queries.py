import strawberry
from typing import List, Optional
from customers.types import CustomerType, CustomerGroupType, CustomerAddressType
from customers.services import CustomerService


@strawberry.type
class Query:

    @strawberry.field
    def customer_groups(self) -> List[CustomerGroupType]:
        """استرجاع جميع فئات العملاء"""
        return CustomerService.get_all_groups()

    @strawberry.field
    def customers(self) -> List[CustomerType]:
        """استرجاع قائمة جميع العملاء"""
        return CustomerService.get_all_customers()

    @strawberry.field
    def customer(self, id: int) -> Optional[CustomerType]:
        """استرجاع تفاصيل عميل محدد برقم الـ ID"""
        return CustomerService.get_customer_by_id(id)