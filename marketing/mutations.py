import strawberry
from marketing.types import (
    CouponType, PromotionType, GiftCardType, LoyaltyTransactionType,
    CouponInput, PromotionInput, GiftCardInput, LoyaltyTransactionInput
)
from marketing.services import MarketingService

@strawberry.type
class Mutation:

    @strawberry.mutation
    def create_coupon(self, input: CouponInput) -> CouponType:
        """إنشاء كوبون خصم جديد"""
        data = {
            "code": input.code,
            "discount_type": input.discount_type,
            "discount_value": input.discount_value,
            "min_order_amount": input.min_order_amount,
            "usage_limit": input.usage_limit,
            "start_date": input.start_date,
            "end_date": input.end_date,
            "is_active": input.is_active,
        }
        return MarketingService.create_coupon(data)

    @strawberry.mutation
    def create_promotion(self, input: PromotionInput) -> PromotionType:
        """إنشاء حملة ترويجية جديدة وتحديد الفئات أو المنتجات المستهدفة"""
        data = {
            "name": input.name,
            "discount_type": input.discount_type,
            "discount_value": input.discount_value,
            "start_date": input.start_date,
            "end_date": input.end_date,
            "is_active": input.is_active,
        }
        return MarketingService.create_promotion(
            data=data,
            group_ids=input.customer_group_ids or [],
            category_ids=input.category_ids or [],
            variant_ids=input.product_variant_ids or []
        )

    @strawberry.mutation
    def create_gift_card(self, input: GiftCardInput) -> GiftCardType:
        """إصدار بطاقة هدايا جديدة"""
        data = {
            "code": input.code,
            "initial_balance": input.initial_balance,
            "customer_id": input.customer_id,
            "expires_at": input.expires_at,
        }
        return MarketingService.create_gift_card(data)

    @strawberry.mutation
    def create_loyalty_transaction(self, input: LoyaltyTransactionInput) -> LoyaltyTransactionType:
        """إضافة أو خصم نقاط ولاء لعميل"""
        data = {
            "customer_id": input.customer_id,
            "order_id": input.order_id,
            "transaction_type": input.transaction_type,
            "points": input.points,
            "notes": input.notes,
        }
        return MarketingService.create_loyalty_transaction(data)