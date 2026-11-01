import strawberry
import strawberry_django

from .inputs import (
    ProductInput,
    ProductVariantInput,
)

from .types import (
    ProductType,
    ProductVariantType,
)

from .services import (
    create_product_service,
    create_variant_service,
)


@strawberry.type
class CatalogMutation:

    @strawberry_django.mutation
    def create_product(
        self,
        data: ProductInput,
    ) -> ProductType:

        return create_product_service(data)

    @strawberry_django.mutation
    def create_variant(
        self,
        data: ProductVariantInput,
    ) -> ProductVariantType:

        return create_variant_service(data)