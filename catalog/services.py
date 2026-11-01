from django.db import transaction
from django.core.exceptions import ValidationError

from .models import (
    Category,
    Brand,
    Product,
    ProductVariant,
    AttributeValue,
)


def get_all_products():
    return Product.objects.select_related(
        "category",
        "brand",
    ).prefetch_related(
        "variants__attribute_values__attribute",
        "images",
    )


def get_product_by_id(product_id: int):
    return get_all_products().filter(
        id=product_id
    ).first()


def get_all_categories():
    return Category.objects.filter(
        is_active=True
    )


def get_all_brands():
    return Brand.objects.filter(
        is_active=True
    )


def create_product_service(data):
    category = Category.objects.get(
        id=data.category_id
    )

    brand = None

    if data.brand_id is not None:
        brand = Brand.objects.get(
            id=data.brand_id
        )

    return Product.objects.create(
        name=data.name,
        slug=data.slug,
        description=data.description,
        category=category,
        brand=brand,
        is_active=data.is_active,
    )


@transaction.atomic
def create_variant_service(data):

    product = Product.objects.get(
        id=data.product_id
    )

    attribute_ids = data.attribute_value_ids or []

    if len(attribute_ids) != len(set(attribute_ids)):
        raise ValidationError(
            "Duplicate attribute value IDs are not allowed."
        )

    values = list(
        AttributeValue.objects.filter(
            id__in=attribute_ids
        )
    )

    if len(values) != len(attribute_ids):
        raise ValidationError(
            "One or more attribute values do not exist."
        )

    attributes = [
        value.attribute_id
        for value in values
    ]

    if len(attributes) != len(set(attributes)):
        raise ValidationError(
            "A variant cannot contain multiple values "
            "for the same attribute."
        )

    if data.price < 0:
        raise ValidationError(
            "Price cannot be negative."
        )

    if (
        data.compare_at_price is not None
        and data.compare_at_price < data.price
    ):
        raise ValidationError(
            "Compare-at price cannot be below sale price."
        )

    variant = ProductVariant.objects.create(
        product=product,
        sku=data.sku,
        price=data.price,
        compare_at_price=data.compare_at_price,
        is_active=data.is_active,
    )

    variant.attribute_values.set(values)

    return variant