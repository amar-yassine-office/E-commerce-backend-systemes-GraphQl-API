from strawberry.permission import BasePermission
from strawberry.types import Info


class IsAuthenticated(BasePermission):

    message = "Authentication required"

    def has_permission(
        self,
        source,
        info: Info,
        **kwargs
    ) -> bool:

        user = info.context.request.user

        return user.is_authenticated