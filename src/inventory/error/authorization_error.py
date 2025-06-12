from graphql import GraphQLError
from typing import Optional, List


class AuthorizationError(GraphQLError):
    """
    Wird ausgelöst, wenn die Authentifizierung zwar vorhanden ist, aber die Berechtigung fehlt (z. B. Rolle).
    """

    def __init__(
        self,
        required_roles: Optional[List[str]] = None,
        user_roles: Optional[List[str]] = None,
    ):
        required_roles_str = ", ".join(required_roles or [])
        user_roles_str = ", ".join(user_roles or [])
        message = (
            f"Zugriff verweigert – benötigte Rollen: [{required_roles_str}] – "
            f"deine Rollen: [{user_roles_str}]"
        )
        super().__init__(message)
