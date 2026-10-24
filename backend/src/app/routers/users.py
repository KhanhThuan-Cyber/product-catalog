from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.core.security import get_password_hash
from app.models.role import Role
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    RoleCreate,
    RoleResponse,
    UserCreateByAdmin,
    UserResponse,
    UserRoleUpdate,
    UserStatusUpdate,
)

router = APIRouter(prefix="/users", tags=["User Management"])
user_repo = UserRepository()
role_repo = RoleRepository()


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Lấy danh sách tất cả người dùng (Yêu cầu Admin)",
    dependencies=[Depends(require_admin)],
)
def list_users(db: Session = Depends(get_db)):
    """API dành riêng cho Admin để xem danh sách toàn bộ người dùng trong hệ thống."""
    users = user_repo.list_all(db)
    return [UserResponse.from_orm_model(u) for u in users]


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo tài khoản người dùng mới bởi Admin (Yêu cầu Admin)",
    dependencies=[Depends(require_admin)],
)
def create_user_by_admin(
    data: UserCreateByAdmin,
    db: Session = Depends(get_db),
):
    """Admin tạo tài khoản người dùng mới và phân quyền trực tiếp."""
    clean_email = data.email.strip().lower()

    if user_repo.get_by_email(db, clean_email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Địa chỉ email này đã tồn tại trong hệ thống",
        )

    target_role = role_repo.get_by_id(db, data.role_id)
    if not target_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vai trò được chọn không tồn tại",
        )

    hashed_password = get_password_hash(data.password)
    new_user = User(
        email=clean_email,
        full_name=data.full_name.strip() if data.full_name else None,
        password_hash=hashed_password,
        role_id=data.role_id,
        is_active=True,
    )

    user_repo.create(db, new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse.from_orm_model(new_user)


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
    summary="Bật / Tắt trạng thái kích hoạt của người dùng (Yêu cầu Admin)",
    dependencies=[Depends(require_admin)],
)
def toggle_user_status(
    user_id: int,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
):
    """Admin có thể khóa hoặc mở khóa tài khoản người dùng bất kỳ."""
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )
    updated_user = user_repo.update_status(db, user, data.is_active)
    return UserResponse.from_orm_model(updated_user)


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    summary="Thay đổi vai trò người dùng (User <-> Admin) (Yêu cầu Admin)",
    dependencies=[Depends(require_admin)],
)
def change_user_role(
    user_id: int,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
):
    """Admin có thể thăng cấp hoặc giáng cấp vai trò của người dùng."""
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )

    target_role = role_repo.get_by_id(db, data.role_id)
    if not target_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vai trò (Role) không tồn tại",
        )

    updated_user = user_repo.update_role(db, user, data.role_id)
    return UserResponse.from_orm_model(updated_user)


@router.get(
    "/roles",
    response_model=list[RoleResponse],
    summary="Lấy danh sách các vai trò khả dụng trong hệ thống",
)
@router.get(
    "/roles/all",
    response_model=list[RoleResponse],
    summary="Lấy danh sách các vai trò khả dụng trong hệ thống (Tương thích)",
)
def list_roles(db: Session = Depends(get_db)):
    """Trả về danh sách tất cả các vai trò trong hệ thống."""
    return role_repo.list_all(db)


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo vai trò (Role) mới trong hệ thống (Yêu cầu Admin)",
    dependencies=[Depends(require_admin)],
)
def create_role(
    data: RoleCreate,
    db: Session = Depends(get_db),
):
    """Admin tạo thêm vai trò mới (ví dụ: manager, staff, editor,...)."""
    clean_name = data.name.strip().lower()

    existing_role = role_repo.get_by_name(db, clean_name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Vai trò '{clean_name}' đã tồn tại trong hệ thống",
        )

    new_role = Role(
        name=clean_name,
        description=data.description.strip() if data.description else None,
    )
    role_repo.create(db, new_role)
    db.commit()
    db.refresh(new_role)
    return new_role
