from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.product import (
    ProductCreate,
    ProductPatch,
    ProductResponse,
    ProductUpdate,
)
from app.schemas.product_filter import ProductFilter
from app.schemas.sorting import ProductSortBy, SortOrder
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])
service = ProductService()


@router.get("", response_model=PaginatedResponse[ProductResponse])
def list_products(
    page: int = Query(
        default=1,
        ge=1,
        description="Số thứ tự trang hiện tại (bắt đầu từ 1)",
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Số lượng sản phẩm trên mỗi trang (tối đa 100)",
    ),
    search: str | None = Query(
        default=None,
        max_length=100,
        description="Tìm kiếm theo tên sản phẩm (không phân biệt chữ hoa/thường)",
    ),
    category_id: int | None = Query(
        default=None,
        gt=0,
        description="Lọc theo mã danh mục sản phẩm (category_id > 0)",
    ),
    min_price: Decimal | None = Query(
        default=None,
        ge=0,
        description="Giá sản phẩm thấp nhất (>= 0)",
    ),
    max_price: Decimal | None = Query(
        default=None,
        ge=0,
        description="Giá sản phẩm cao nhất (>= 0)",
    ),
    sort_by: ProductSortBy = Query(
        default=ProductSortBy.id,
        description="Trường cần sắp xếp: id, price, created_at, name",
    ),
    order: SortOrder = Query(
        default=SortOrder.asc,
        description="Chiều sắp xếp: asc (tăng dần) hoặc desc (giảm dần)",
    ),
    db: Session = Depends(get_db),
):
    try:
        filter_params = ProductFilter(
            search=search,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            order=order,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    pagination_params = PaginationParams(page=page, page_size=page_size)
    return service.list_products_paginated(
        db=db,
        filter_params=filter_params,
        pagination=pagination_params,
    )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    return service.get_product(db, product_id)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
):
    return service.create_product(db, data)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
):
    return service.update_product(db, product_id, data)


@router.patch("/{product_id}", response_model=ProductResponse)
def patch_product(
    product_id: int,
    data: ProductPatch,
    db: Session = Depends(get_db),
):
    return service.patch_product(db, product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    service.delete_product(db, product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
