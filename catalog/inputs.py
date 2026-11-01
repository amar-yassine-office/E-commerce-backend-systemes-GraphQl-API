import strawberry
from decimal import Decimal


@strawberry.input
class CategoryInput:
    name: str
    slug: str
    parent_id: int | None = None
    is_active: bool = True


@strawberry.input
class BrandInput:
    name: str
    slug: str
    is_active: bool = True


@strawberry.input
class ProductInput:
    name: str
    slug: str
    description: str
    category_id: int
    brand_id: int | None = None
    is_active: bool = True


@strawberry.input
class AttributeInput:
    name: str


@strawberry.input
class AttributeValueInput:
    attribute_id: int
    value: str


@strawberry.input
class ProductVariantInput:
    product_id: int
    sku: str
    price: Decimal
    compare_at_price: Decimal | None = None
    attribute_value_ids: list[int] | None = None
    is_active: bool = True