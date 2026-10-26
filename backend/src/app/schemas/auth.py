from datetime import datetime
from typing import Annotated
from pydantic import (AfterValidator, AliasPath, BaseModel, ConfigDict, Field)


EmailAddress = Annotated[
    str,
    Field(
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        max_length=150,
        description="Địa chỉ email hợp lệ",
    ),
]

NewPassword = Annotated[
    str,
    Field(
        min_length=6,
        max_length=100,
        description="Mật khẩu từ 6 đến 100 ký tự",
    ),
]


def normalize_full_name(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Full name không được để trống")
    return value


# Dùng cho tên người dùng: cho phép dấu cách và ký tự unicode (tên tiếng Việt)
FullName = Annotated[
    str,
    Field(
        min_length=1,
        max_length=100,
        description="Họ và tên đầy đủ",
    ),
    AfterValidator(normalize_full_name),
]

# Dùng riêng cho tên vai trò: chỉ cho phép chữ cái, số, _ hoặc -
RoleName = Annotated[
    str,
    Field(
        min_length=2,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Tên vai trò: chữ cái, số, _ hoặc -",
    ),
]


class UserRegister(BaseModel):
    email: EmailAddress
    password: NewPassword
    full_name: FullName | None = None


class UserLogin(BaseModel):
    email: EmailAddress
    password: str = Field(min_length=1, max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RoleCreate(BaseModel):
    name: RoleName
    description: str | None = Field(default=None, max_length=255)


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """Thông tin người dùng, không bao gồm mật khẩu."""
    id: int
    email: str
    full_name: str | None = None
    is_active: bool
    role_id: int
    role_name: str | None = Field(
        default=None,
        validation_alias=AliasPath("role", "name"),
    )
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_model(cls, user) -> "UserResponse":
        return cls.model_validate(user)


class UserStatusUpdate(BaseModel):
    """Cập nhật trạng thái hoạt động."""
    is_active: bool


class UserRoleUpdate(BaseModel):
    """Cập nhật vai trò."""
    role_id: int = Field(gt=0)


class UserProfileUpdate(BaseModel):
    """Cập nhật họ tên."""
    full_name: FullName


class ChangePasswordRequest(BaseModel):
    """Đổi mật khẩu."""
    old_password: str = Field(min_length=1, max_length=100)
    new_password: NewPassword


class UserCreateByAdmin(UserRegister):
    """Dữ liệu tạo tài khoản bởi quản trị viên."""
    role_id: int = Field(gt=0, description="ID vai trò")
