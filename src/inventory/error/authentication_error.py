from graphql import GraphQLError
from typing import Optional


class AuthenticationError(GraphQLError):
    """
    Wird ausgelöst, wenn keine oder eine ungültige Authentifizierung vorliegt (z.B. kein Token).
    """

    def __init__(self, message: Optional[str] = None):
        default_message = "Kein Authentifizierungs-Token vorhanden oder ungültig."
        super().__init__(message or default_message)
