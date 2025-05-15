"""Exceptions in der Geschäftslogik."""

from collections.abc import Mapping

from graphql import GraphQLError

__all__ = [
    "EmailExistsError",
    "NotAllowedError",
    "NotFoundError",
    "UsernameExistsError",
    "VersionOutdatedError",
]


class AuthenticationError(GraphQLError):
    def __init__(self, message="Authentication required!"):
        super().__init__(message)


class EmailExistsError(Exception):
    """Exception, falls die Emailadresse bereits existiert."""

    def __init__(self, email: str) -> None:
        """Initialisierung von EmailExistsError mit der Emailadresse.

        :param email: Bereits existierende Emailadresse
        """
        super().__init__(f"Existierende Email: {email}")
        self.email = email


class UsernameExistsError(Exception):
    """Exception, falls der Benutzername bereits existiert."""

    def __init__(self, username: str) -> None:
        """Initialisierung von UsernameExistsError mit dem Benutzernamen.

        :param username: Bereits existierender Benutzername
        """
        super().__init__(f"Existierender Benutzername: {username}")
        self.username = username


class NotAllowedError(Exception):
    """Exception, falls es der Zugriff nicht erlaubt ist."""


class NotFoundError(Exception):
    """Exception, falls kein Patient gefunden wurde."""

    def __init__(
        self,
        patient_id: int | None = None,
        suchkriterien: Mapping[str, str] | None = None,
    ) -> None:
        """Initialisierung von NotFoundError mit ID und Suchkriterien.

        :param patient_id: Patient-ID, zu der nichts gefunden wurde
        :param suchkriterien: Suchkriterien, zu denen nichts gefunden wurde
        """
        super().__init__("Not Found")
        self.patient_id = patient_id
        self.suchkriterien = suchkriterien


class VersionOutdatedError(Exception):
    """Exception, falls die Versionsnummer beim Aktualisieren veraltet ist."""

    def __init__(self, version: int) -> None:
        """Initialisierung von VersionOutdatedError mit veralteter Versionsnummer.

        :param version: Veraltete Versionsnummer
        """
        super().__init__(f"Veraltete Version: {version}")
        self.version = version
