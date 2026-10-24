from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserRegister(BaseModel):
    """Schema đăng ký tài khoản mới."""
    email: str = Field(
        ...,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        max_length=150,
        description="Địa chỉ email hợp lệ",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Mật khẩu tối thiểu 6 ký tự",
        examples=["Password@123"],
    )
    full_name: str | None = Field(
        default=None,
        max_length=100,
        description="Họ và tên người dùng",
        examples=["Nguyễn Văn A"],
    )


class UserLogin(BaseModel):
    """Schema đăng nhập tài khoản."""
    email: str = Field(
        ...,
        description="Email đăng nhập",
    )
    password: str = Field(
        ...,
        description="Mật khẩu",
    )


class TokenResponse(BaseModel):
    """Schema phản hồi Access Token JWT."""
    access_token: str
    token_type: str = "bearer"


class RoleCreate(BaseModel):
    """Schema tạo vai trò mới."""
    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_\-]+$",
        description="Tên vai trò (chữ cái, số, gạch dưới hoặc gạch nối)",
        examples=["manager", "staff", "editor"],
    )
    description: str | None = Field(
        default=None,
        max_length=255,
        description="Mô tả chức năng của vai trò",
        examples=["Quản lý đơn hàng và hỗ trợ khách hàng"],
    )


class RoleResponse(BaseModel):
    """Schema thông tin vai trò."""
    id: int
    name: str
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """Schema thông tin người dùng trả về."""
    id: int
    email: str
    full_name: str | None = None
    is_active: bool
    role_id: int
    role_name: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_model(cls, user) -> "UserResponse":
        """Factory method trích xuất role_name từ quan hệ relationship Role."""
        role_name = user.role.name if getattr(user, "role", None) else None
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            role_id=user.role_id,
            role_name=role_name,
            created_at=user.created_at,
        )


class UserStatusUpdate(BaseModel):
    """Schema cập nhật trạng thái hoạt động của User."""
    is_active: bool


class UserRoleUpdate(BaseModel):
    """Schema cập nhật vai trò của User."""
    role_id: int = Field(gt=0)


class UserProfileUpdate(BaseModel):
    """Schema cập nhật thông tin cá nhân của người dùng."""
    full_name: str = Field(min_length=1, max_length=100, description="Họ và tên mới")


class ChangePasswordRequest(BaseModel):
    """Schema đổi mật khẩu cá nhân."""
    old_password: str = Field(description="Mật khẩu hiện tại")
    new_password: str = Field(min_length=6, max_length=100, description="Mật khẩu mới tối thiểu 6 ký tự")


class UserCreateByAdmin(BaseModel):
    """Schema tạo tài khoản mới bởi Quản trị viên."""
    email: str = Field(
        ...,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        max_length=150,
        description="Địa chỉ email hợp lệ",
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Mật khẩu khởi tạo tối thiểu 6 ký tự",
    )
    full_name: str | None = Field(default=None, max_length=100, description="Họ và tên")
    role_id: int = Field(gt=0, description="ID vai trò (Role)")
