from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
from typing import List, Optional
import os
import httpx
from loguru import logger


class KeycloakService:
    """
    Service zur Extraktion und Validierung von JWTs aus Keycloak,
    inklusive dynamischem Laden des öffentlichen Schlüssels via JWKS-Endpunkt.
    Unterstützt das Überspringen von Introspection Queries.
    """

    def __init__(self, request: Request, token: Optional[str], payload: dict):
        self.request = request
        self.token = token
        self.payload = payload

    @classmethod
    async def create(cls, request: Request) -> "KeycloakService":
        """
        Erstellt eine Instanz des KeycloakService. Bei IntrospectionQuery wird
        keine Authentifizierung erzwungen.
        """
        if await cls._is_introspection_request(request):
            logger.debug(
                "🔍 IntrospectionQuery erkannt – Authentifizierung übersprungen."
            )
            return cls(request, None, {})

        try:
            token = cls._extract_token(request)
            payload = await cls._decode_token(token)
            return cls(request, token, payload)
        except HTTPException as e:
            logger.warning("Keycloak Token-Fehler: {}", e.detail)
            raise

    @classmethod
    async def _is_introspection_request(cls, request: Request) -> bool:
        """
        Erkennt sowohl normale IntrospectionQuerys als auch Apollo-Gateway-Aufrufe
        anhand eines speziellen Headers.
        """
        if request.headers.get("x-introspection") == "true":
            logger.debug("🔍 Gateway-Introspection via Header erkannt.")
            return True
    
        if request.method != "POST":
            return False
        try:
            body = await request.json()
            if body.get("operationName") == "IntrospectionQuery":
                logger.debug("🔍 Standard-IntrospectionQuery erkannt.")
                return True
        except Exception:
            pass
        return False


    @classmethod
    def _extract_token(cls, request: Request) -> str:
        """
        Extrahiert das Bearer-Token aus dem Authorization-Header.
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Kein gültiger Bearer-Token gefunden",
            )
        return auth_header.removeprefix("Bearer ").strip()

    @classmethod
    async def _decode_token(cls, token: str) -> dict:
        """
        Dekodiert und verifiziert das JWT mithilfe der JWKS von Keycloak.
        """
        realm = os.getenv("KC_SERVICE_REALM", "gentlecorp")
        host = os.getenv("KC_SERVICE_HOST", "localhost")
        port = os.getenv("KC_SERVICE_PORT", "18080")

        jwks_url = (
            f"http://{host}:{port}/auth/realms/{realm}/protocol/openid-connect/certs"
        )
        logger.debug("Keycloak JWKS URI: {}", jwks_url)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(jwks_url)
            jwks = response.json()

            keys = jwks.get("keys")
            if not keys:
                raise ValueError("JWKS enthält keine Schlüssel")

            unverified_header = jwt.get_unverified_header(token)
            for key in keys:
                if key["kid"] == unverified_header["kid"]:
                    return jwt.decode(
                        token,
                        key,
                        algorithms=["RS256"],
                        options={"verify_aud": False},
                    )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Kein passender Schlüssel im JWKS gefunden",
            )

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token-Verifikation fehlgeschlagen: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fehler beim Laden des JWKS: {e}",
            )

    def get_roles(self) -> List[str]:
        """
        Gibt alle Rollen aus dem realm_access des Tokens zurück.
        """
        return self.payload.get("realm_access", {}).get("roles", [])

    def has_role(self, required_roles: List[str]) -> bool:
        """
        Prüft, ob eine der erforderlichen Rollen vorhanden ist.
        """
        return any(role in self.get_roles() for role in required_roles)

    def assert_roles(self, required_roles: List[str]) -> None:
        """
        Wirft einen Fehler, wenn keine der erforderlichen Rollen vorhanden ist.
        """
        if not self.has_role(required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Zugriff verweigert – Rollen {required_roles} erforderlich",
            )
