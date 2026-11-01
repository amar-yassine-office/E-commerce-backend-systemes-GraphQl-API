import strawberry
from typing import List, Optional
from orders.types import OrderType, ReturnOrderType
from orders.services import OrderService

@strawberry.type
class Query:

    @strawberry.field
    def orders(self) -> List[OrderType]:
        """استرجاع قائمة جميع الطلبات"""
        return OrderService.get_all_orders()

    @strawberry.field
    def order(self, id: int) -> Optional[OrderType]:
        """استرجاع تفاصيل طلب محدد برقم الـ ID"""
        return OrderService.get_order_by_id(id)