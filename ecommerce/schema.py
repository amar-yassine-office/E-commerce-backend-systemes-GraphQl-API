import strawberry

# تأكد من اسم الكلاس الموجود فعلياً داخل ملف catalog/queries.py
from catalog.queries import CatalogQuery as QueryCatalog
from customers.queries import Query as CustomerQuery
from inventory.queries import Query as InventoryQuery
from marketing.queries import Query as MarketingQuery
from marketing.mutations import Mutation as MarketingMutation

from catalog.mutations import CatalogMutation as MutationCatalog
from customers.mutations import Mutation as CustomerMutation
from inventory.mutations import Mutation as InventoryMutation
from orders.queries import Query as OrderQuery      # لاحظ هنا مفرد OrderQuery أو جمع حسب ما كتبته
from orders.mutations import Mutation as OrderMutation
from accountante.queries import AccountanteQuery
from accountante.mutations import AccountanteMutation
from payments.queries import PaymentQuery
from payments.mutations import PaymentMutation
from shipping.queries import ShippingQuery
from shipping.mutations import ShippingMutation
from gqlauth.core.middlewares import JwtSchema
@strawberry.type
class Query(QueryCatalog, CustomerQuery, InventoryQuery, MarketingQuery, OrderQuery,AccountanteQuery , PaymentQuery,ShippingQuery ):
    pass



@strawberry.type
class Mutation(MutationCatalog, CustomerMutation, InventoryMutation, MarketingMutation, OrderMutation ,AccountanteMutation,PaymentMutation,ShippingMutation ):
    pass

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
#the protection  of the api's
schema = JwtSchema(
    query=Query,
    mutation=Mutation,
)