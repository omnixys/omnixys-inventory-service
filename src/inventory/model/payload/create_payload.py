import strawberry


@strawberry.type
class CreatePayload:
    """Resultat-Typ, wenn ein neuer Patient angelegt wurde."""

    id: int
    """ID des neu angelegten Inventory"""
