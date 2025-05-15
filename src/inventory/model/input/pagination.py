# src/product/model/input/pagination.py

import strawberry


@strawberry.input
class PaginationInput:
    """GraphQL Input-Typ für Pagination."""

    skip: int | None = 0
    limit: int | None = 10
