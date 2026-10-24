import pytest
from pydantic import ValidationError

from app.schemas.pagination import PaginatedResponse, PaginationParams


def test_pagination_params_defaults():
    params = PaginationParams()
    assert params.page == 1
    assert params.page_size == 10
    assert params.offset == 0
    assert params.limit == 10


def test_pagination_params_custom_values():
    params = PaginationParams(page=3, page_size=25)
    assert params.page == 3
    assert params.page_size == 25
    assert params.offset == 50
    assert params.limit == 25


def test_pagination_params_validation_errors():
    # page must be >= 1
    with pytest.raises(ValidationError):
        PaginationParams(page=0)

    # page_size must be >= 1 and <= 100
    with pytest.raises(ValidationError):
        PaginationParams(page_size=0)

    with pytest.raises(ValidationError):
        PaginationParams(page_size=101)


def test_paginated_response_create_factory():
    items = ["item1", "item2", "item3"]
    params = PaginationParams(page=2, page_size=5)

    response = PaginatedResponse[str].create(
        items=items,
        total=13,
        page=params,
    )

    assert response.items == items
    assert response.total == 13
    assert response.page == 2
    assert response.page_size == 5
    assert response.total_pages == 3


def test_paginated_response_create_with_zero_total():
    response = PaginatedResponse[str].create(
        items=[],
        total=0,
        page=1,
        page_size=10,
    )

    assert response.items == []
    assert response.total == 0
    assert response.page == 1
    assert response.page_size == 10
    assert response.total_pages == 0


def test_paginated_response_validation():
    # total cannot be negative
    with pytest.raises(ValidationError):
        PaginatedResponse[str](
            items=["a"],
            total=-1,
            page=1,
            page_size=10,
            total_pages=1,
        )
