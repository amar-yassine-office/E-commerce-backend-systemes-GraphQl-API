import strawberry
import strawberry_django

from .models import Product, Category, Brand

from .types import (
    ProductType,
    CategoryType,
    BrandType,
)


@strawberry.type
class CatalogQuery:

    @strawberry_django.field
    def products(self) -> list[ProductType]:
        return Product.objects.filter(
            is_active=True
        )

    @strawberry_django.field
    def product(
        self,
        product_id: int,
    ) -> ProductType | None:

        return Product.objects.filter(
            id=product_id,
            is_active=True,
        ).first()

    @strawberry_django.field
    def categories(self) -> list[CategoryType]:
        return Category.objects.filter(
            is_active=True
        )

    @strawberry_django.field
    def brands(self) -> list[BrandType]:
        return Brand.objects.filter(
            is_active=True
        )