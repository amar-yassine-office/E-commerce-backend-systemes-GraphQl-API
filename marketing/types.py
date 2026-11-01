import strawberry
from decimal import Decimal
from typing import List, Optional

from marketing.models import Coupon, Promotion, GiftCard, LoyaltyTransaction
from customers.types import CustomerType, CustomerGroupType
from catalog.types import CategoryType, ProductVariantType


@strawberry.django.type(Coupon)
class CouponType:
    id: strawberry.ID
    code: str
    discount_type: str
    discount_value: Decimal
    min_order_amount: Decimal
    usage_limit: int
    times_used: int
    start_date: str
    end_date: str
    is_active: bool


@strawberry.django.type(Promotion)
class PromotionType:
    id: strawberry.ID
    name: str
    discount_type: str
    discount_value: Decimal
    start_date: str
    end_date: str
    is_active: bool

    # العلاقات
    customer_groups: List[CustomerGroupType]
    categories: List[CategoryType]
    product_variants: List[ProductVariantType]


@strawberry.django.type(GiftCard)
class GiftCardType:
    id: strawberry.ID
    code: str
    initial_balance: Decimal
    current_balance: Decimal
    customer: Optional[CustomerType]
    expires_at: str
    is_active: bool
    created_at: str


@strawberry.django.type(LoyaltyTransaction)
class LoyaltyTransactionType:
    id: strawberry.ID
    customer: CustomerType
    transaction_type: str
    points: int
    notes: Optional[str]
    created_at: str


# --- Input Types للـ Mutations ---

@strawberry.input
class CouponInput:
    code: str
    discount_type: str
    discount_value: Decimal
    min_order_amount: Optional[Decimal] = Decimal('0.00')
    usage_limit: Optional[int] = 0
    start_date: str
    end_date: str
    is_active: Optional[bool] = True


@strawberry.input
class PromotionInput:
    name: str
    discount_type: str
    discount_value: Decimal
    start_date: str
    end_date: str
    is_active: Optional[bool] = True
    customer_group_ids: Optional[List[int]] = None
    category_ids: Optional[List[int]] = None
    product_variant_ids: Optional[List[int]] = None


@strawberry.input
class GiftCardInput:
    code: str
    initial_balance: Decimal
    customer_id: Optional[int] = None
    expires_at: str


@strawberry.input
class LoyaltyTransactionInput:
    customer_id: int
    order_id: Optional[int] = None
    transaction_type: str
    points: int
    notes: Optional[str] = None