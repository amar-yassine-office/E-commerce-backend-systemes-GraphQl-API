from typing import List, Optional
from marketing.models import Coupon, Promotion, GiftCard, LoyaltyTransaction

class MarketingService:

    # --- الكوبونات (Coupons) ---
    @staticmethod
    def get_all_coupons() -> List[Coupon]:
        return Coupon.objects.all()

    @staticmethod
    def create_coupon(data: dict) -> Coupon:
        return Coupon.objects.create(**data)

    # --- الحملات الترويجية (Promotions) ---
    @staticmethod
    def get_all_promotions() -> List[Promotion]:
        return Promotion.objects.prefetch_related('customer_groups', 'categories', 'product_variants').all()

    @staticmethod
    def create_promotion(data: dict, group_ids: list, category_ids: list, variant_ids: list) -> Promotion:
        promotion = Promotion.objects.create(**data)
        if group_ids:
            promotion.customer_groups.set(group_ids)
        if category_ids:
            promotion.categories.set(category_ids)
        if variant_ids:
            promotion.product_variants.set(variant_ids)
        return promotion

    # --- بطاقات الهدايا (Gift Cards) ---
    @staticmethod
    def get_all_gift_cards() -> List[GiftCard]:
        return GiftCard.objects.select_related('customer').all()

    @staticmethod
    def create_gift_card(data: dict) -> GiftCard:
        # تعيين الرصيد الحالي ليكون مساوياً للرصيد الأساسي عند الإصدار
        data['current_balance'] = data['initial_balance']
        return GiftCard.objects.create(**data)

    # --- نقاط الولاء (Loyalty Transactions) ---
    @staticmethod
    def get_customer_loyalty_history(customer_id: int) -> List[LoyaltyTransaction]:
        return LoyaltyTransaction.objects.filter(customer_id=customer_id).select_related('customer', 'order')

    @staticmethod
    def create_loyalty_transaction(data: dict) -> LoyaltyTransaction:
        return LoyaltyTransaction.objects.create(**data)