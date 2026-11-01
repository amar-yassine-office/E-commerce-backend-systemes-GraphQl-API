import strawberry_django
from strawberry import auto

from .models import (
    Category,
    Brand,
    Product,
    Attribute,
    AttributeValue,
    ProductVariant,
    ProductImage,
)


@strawberry_django.type(Category)
class CategoryType:
    id: auto
    name: auto
    slug: auto
    is_active: auto
    parent: "CategoryType | None"


@strawberry_django.type(Brand)
class BrandType:
    id: auto
    name: auto
    slug: auto
    is_active: auto


@strawberry_django.type(Attribute)
class AttributeType:
    id: auto
    name: auto


@strawberry_django.type(AttributeValue)
class AttributeValueType:
    id: auto
    attribute: AttributeType
    value: auto


@strawberry_django.type(ProductVariant)
class ProductVariantType:
    id: auto
    sku: auto
    price: auto
    compare_at_price: auto
    is_active: auto
    attribute_values: list[AttributeValueType]


@strawberry_django.type(ProductImage)
class ProductImageType:
    id: auto
    is_feature: auto


@strawberry_django.type(Product)
class ProductType:
    id: auto
    name: auto
    slug: auto
    description: auto

    category: CategoryType
    brand: BrandType | None

    variants: list[ProductVariantType]
    images: list[ProductImageType]

    is_active: auto
    created_at: auto
    updated_at: auto