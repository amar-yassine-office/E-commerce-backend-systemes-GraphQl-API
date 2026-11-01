import strawberry
from typing import List
from marketing.types import CouponType, PromotionType, GiftCardType, LoyaltyTransactionType
from marketing.services import MarketingService

@strawberry.type
class Query:

    @strawberry.field
    def coupons(self) -> List[CouponType]:
        """استرجاع جميع كوبونات الخصم"""
        return MarketingService.get_all_coupons()

    @strawberry.field
    def promotions(self) -> List[PromotionType]:
        """استرجاع جميع الحملات الترويجية"""
        return MarketingService.get_all_promotions()

    @strawberry.field
    def gift_cards(self) -> List[GiftCardType]:
        """استرجاع جميع بطاقات الهدايا"""
        return MarketingService.get_all_gift_cards()

    @strawberry.field
    def customer_loyalty_transactions(self, customer_id: int) -> List[LoyaltyTransactionType]:
        """استرجاع سجل نقاط الولاء لعميل معين"""
        return MarketingService.get_customer_loyalty_history(customer_id)