# Backend — Product Management API

Hệ thống Backend RESTful API hiệu năng cao được xây dựng trên nền tảng **FastAPI (Python 3.11+)**, **SQLAlchemy ORM 2.0**, **Pydantic v2** và hệ thống phân quyền theo vai trò (RBAC - Role-Based Access Control) kết hợp cơ chế tự động hóa khởi tạo Database (Auto-migration & Data Bootstrapping).

---

## 1. Kiến trúc phân tầng (Layered Architecture)

Backend được tổ chức theo mô hình kiến trúc phân tầng 3 lớp chuẩn doanh nghiệp (**Layered / Onion Architecture**), phân tách rõ ràng trách nhiệm giữa các tầng:

```
FastAPI Client / Frontend
        │
        ▼ (HTTP Request / JSON)
┌────────────────────────────────────────────────────────┐
│ 1. API & ROUTER LAYER (FastAPI Routers)                │
│    - routers/auth.py, users.py, products.py, ...       │
│    - Dependency Injection: get_db, require_admin       │
│    - Pydantic Validation & Serialization (Schemas)     │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼ (Data Transfer Objects - DTOs)
┌────────────────────────────────────────────────────────┐
│ 2. SERVICE LAYER (Business Logic)                      │
│    - services/product_service.py, category_service.py  │
│    - Kiểm tra logic nghiệp vụ, transaction management │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼ (SQLAlchemy Queries)
┌────────────────────────────────────────────────────────┐
│ 3. REPOSITORY LAYER (Data Access Object - DAO)         │
│    - repositories/base_repository.py (Generic OOP)     │
│    - product_repository.py, role_repository.py, ...   │
│    - Xử lý phân trang, lọc ilike, whitelist sort      │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼ (SQLAlchemy ORM Models)
┌────────────────────────────────────────────────────────┐
│ 4. DATABASE & INFRASTRUCTURE LAYER                     │
│    - models/user.py, role.py, category.py, product.py  │
│    - core/init_db.py (Auto-upgrade schema & seeding)   │
│    - SQLite (Dev/Test) / PostgreSQL (Production)       │
└────────────────────────────────────────────────────────┘
```

---

## 2. Cấu trúc thư mục chi tiết

```text
backend/
├── src/
│   └── app/
│       ├── main.py                     # Entry point FastAPI, CORS & startup event
│       ├── api/
│       │   └── deps.py                 # Dependency Injection: get_db, JWT auth & RoleChecker
│       ├── core/
│       │   ├── config.py               # Quản lý biến môi trường (.env) bằng Pydantic Settings
│       │   ├── database.py             # SQLAlchemy Engine, SessionLocal & pool_pre_ping
│       │   ├── init_db.py              # Tự động hóa nâng cấp schema và nạp Super Admin mặc định
│       │   └── security.py             # Hashing mật khẩu (BCrypt) & ký/giải mã JWT token
│       ├── models/                     # SQLAlchemy Declarative Models
│       │   ├── base.py                 # Base declarative class
│       │   ├── role.py                 # Entity Role (id, name, description, created_at)
│       │   ├── user.py                 # Entity User (id, email, password_hash, role_id, is_active)
│       │   ├── category.py             # Entity Category (id, name, description, created_at)
│       │   └── product.py              # Entity Product (id, name, price, stock, category_id, is_active)
│       ├── schemas/                    # Pydantic v2 Data Transfer Objects (DTOs)
│       │   ├── auth.py                 # UserRegister, UserLogin, UserResponse, RoleCreate, RoleResponse
│       │   ├── pagination.py           # Generic PaginatedResponse[T], PaginationParams
│       │   ├── category.py             # CategoryCreate, CategoryUpdate, CategoryResponse
│       │   └── product.py              # ProductCreate, ProductUpdate, ProductPatch, ProductResponse
│       ├── repositories/               # Tầng truy xuất dữ liệu (Data Access Layer)
│       │   ├── base_repository.py      # Lớp cơ sở trừu tượng hỗ trợ phân trang generic paginate()
│       │   ├── role_repository.py      # Truy vấn Role: get_by_name, list_all, create
│       │   ├── user_repository.py      # Truy vấn User: get_by_email, update_status, update_role
│       │   ├── category_repository.py  # Truy vấn Category: get_by_name, list_all, create, delete
│       │   └── product_repository.py   # Truy vấn Product: lọc search, category, khoảng giá, safe sort
│       ├── services/                   # Tầng nghiệp vụ xử lý logic
│       │   ├── category_service.py     # Ràng buộc toàn vẹn dữ liệu, kiểm tra không xóa danh mục có sản phẩm
│       │   └── product_service.py      # Xử lý cập nhật toàn phần (PUT) và từng phần (PATCH)
│       └── routers/                    # Tầng API Endpoints
│           ├── auth.py                 # /Thuancyber/auth (Register, Login, Me, Change Password)
│           ├── users.py                # /Thuancyber/users (List, Create User, Status, Role, Roles CRUD)
│           ├── categories.py           # /Thuancyber/categories (CRUD danh mục)
│           └── products.py             # /Thuancyber/products (CRUD sản phẩm + Filter + Paginate)
├── tests/                              # Bộ kiểm thử tích hợp (Pytest)
│   ├── test_auth_endpoints.py          # Kiểm thử Auth, RBAC, Profile, Admin User & Role Creation
│   └── test_products_categories.py     # Kiểm thử CRUD Category và Product
└── requirements.txt                    # Danh sách thư viện phụ thuộc
```

---

## 3. Tự động hóa Khởi tạo Database (`init_db.py`)

Khi server Backend khởi động (thông qua sự kiện `@app.on_event("startup")` trong [main.py](file:///d:/Product-Catalog/backend/src/app/main.py)), hàm `init_database()` được tự động thực thi với các cơ chế đảm bảo an toàn:

1. **Auto Upgrade Schema:**
   - Tự động kiểm tra cấu trúc bảng `users` hiện hữu trong cơ sở dữ liệu.
   - Nếu phát hiện cột `password_hash` cũ có kích thước `< 255` ký tự, tự động thực thi lệnh `ALTER TABLE users ALTER COLUMN password_hash TYPE VARCHAR(255)` để tương thích chuẩn mã hóa mật khẩu hiện đại mà không làm mất dữ liệu.
   - Tự động gọi `Base.metadata.create_all()` để tạo tất cả các bảng chưa tồn tại (`roles`, `users`, `categories`, `products`).
2. **Idempotent Role Bootstrapping:**
   - Kiểm tra và tự động khởi tạo 2 vai trò cơ sở: `admin` (Quản trị viên toàn quyền) và `user` (Khách hàng mua sắm) nếu chưa có trong DB.
3. **Idempotent Super Admin Bootstrapping:**
   - Kiểm tra xem hệ thống đã có tài khoản Admin chưa. Nếu chưa có, tự động tạo tài khoản Super Admin mặc định:
     - **Email:** `admin@system.local`
     - **Mật khẩu:** `Admin@123456`
     - **Vai trò:** `admin` (Role ID: 1)

---

## 4. Danh mục API Endpoints chi tiết (Prefix: `/Thuancyber`)

Tất cả các route Backend được định tuyến thống nhất dưới tiền tố `/Thuancyber`.

### 4.1. Phân hệ Authentication & Hồ sơ cá nhân (`/Thuancyber/auth`)

| Phương thức | Endpoint | Yêu cầu quyền | Mô tả chi tiết |
|---|---|---|---|
| `POST` | `/auth/register` | Công khai | Đăng ký tài khoản khách hàng mới (mặc định role `user`). |
| `POST` | `/auth/login` | Công khai | Đăng nhập bằng Email & Mật khẩu, trả về JWT Access Token. |
| `GET` | `/auth/me` | Bearer Token | Lấy thông tin tài khoản người dùng hiện đang đăng nhập. |
| `PATCH` | `/auth/me` | Bearer Token | Cập nhật thông tin cá nhân (họ và tên hiển thị). |
| `POST` | `/auth/change-password` | Bearer Token | Đổi mật khẩu cá nhân (yêu cầu mật khẩu cũ chính xác). |

#### Ví dụ Body Đăng Ký (`POST /Thuancyber/auth/register`):
```json
{
  "email": "customer@example.com",
  "password": "SecurePassword@123",
  "full_name": "Nguyễn Văn A"
}
```

#### Ví dụ Response Đăng Nhập (`POST /Thuancyber/auth/login`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 4.2. Phân hệ Quản lý Người dùng & Vai trò (`/Thuancyber/users`)

| Phương thức | Endpoint | Yêu cầu quyền | Mô tả chi tiết |
|---|---|---|---|
| `GET` | `/users` | `Admin` | Lấy danh sách toàn bộ người dùng trong hệ thống. |
| `POST` | `/users` | `Admin` | Admin tạo trực tiếp tài khoản mới và chỉ định vai trò (`role_id`). |
| `PATCH` | `/users/{id}/status` | `Admin` | Khóa hoặc mở khóa tài khoản người dùng (`is_active: bool`). |
| `PATCH` | `/users/{id}/role` | `Admin` | Thay đổi vai trò người dùng (thăng cấp / giáng cấp vai trò). |
| `GET` | `/users/roles` | Mọi người dùng | Lấy danh sách tất cả các vai trò khả dụng trong hệ thống. |
| `POST` | `/users/roles` | `Admin` | **Tạo vai trò mới** động trong hệ thống (manager, staff, editor...). |

#### Ví dụ Body Tạo Role mới (`POST /Thuancyber/users/roles`):
```json
{
  "name": "manager",
  "description": "Quản lý sản phẩm, đơn hàng và danh mục"
}
```

---

### 4.3. Phân hệ Danh mục Sản phẩm (`/Thuancyber/categories`)

| Phương thức | Endpoint | Yêu cầu quyền | Mô tả chi tiết |
|---|---|---|---|
| `GET` | `/categories` | Công khai | Lấy danh sách toàn bộ danh mục sản phẩm. |
| `GET` | `/categories/{id}` | Công khai | Xem thông tin chi tiết một danh mục. |
| `POST` | `/categories` | `Admin` | Tạo danh mục mới (kiểm tra không trùng tên). |
| `PUT` | `/categories/{id}` | `Admin` | Cập nhật tên và mô tả danh mục. |
| `DELETE` | `/categories/{id}` | `Admin` | Xóa danh mục (chặn xóa nếu danh mục đang có sản phẩm). |

---

### 4.4. Phân hệ Sản phẩm (`/Thuancyber/products`)

| Phương thức | Endpoint | Yêu cầu quyền | Mô tả chi tiết |
|---|---|---|---|
| `GET` | `/products` | Công khai | Danh sách sản phẩm (có tìm kiếm, lọc, sắp xếp, phân trang). |
| `GET` | `/products/{id}` | Công khai | Xem thông tin chi tiết sản phẩm theo ID. |
| `POST` | `/products` | `Admin` | Thêm mới sản phẩm vào cơ sở dữ liệu. |
| `PUT` | `/products/{id}` | `Admin` | Cập nhật toàn bộ thông tin sản phẩm. |
| `PATCH` | `/products/{id}` | `Admin` | Cập nhật từng trường riêng lẻ (Partial update). |
| `DELETE` | `/products/{id}` | `Admin` | Xóa sản phẩm khỏi hệ thống. |

#### Tham số Query nâng cao của `GET /Thuancyber/products`:
- `page`: Trang hiện tại (mặc định: `1`, tối thiểu: `1`).
- `page_size`: Kích thước trang (mặc định: `10`, tối đa: `100`).
- `search`: Tìm kiếm gần đúng theo tên sản phẩm (`ilike %keyword%`, không phân biệt chữ hoa/thường).
- `category_id`: Lọc sản phẩm theo ID danh mục.
- `min_price` / `max_price`: Lọc sản phẩm theo khoảng giá bán.
- `sort_by`: Trường sắp xếp được whitelist an toàn (`price`, `created_at`, `name`, `id`).
- `order`: Hướng sắp xếp (`asc` hoặc `desc`).

#### Cấu trúc Response phân trang Generic (`PaginatedResponse[T]`):
```json
{
  "items": [
    {
      "id": 1,
      "name": "Bàn phím cơ không dây",
      "description": "Bàn phím cơ Bluetooth switch êm ái",
      "price": 1250000.0,
      "stock": 35,
      "category_id": 2,
      "is_active": true,
      "created_at": "2026-10-24T10:00:00Z",
      "updated_at": "2026-10-24T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

---

## 5. Cơ chế Bảo Mật & Phân Quyền (RBAC)

1. **Mã hóa mật khẩu:** Mật khẩu người dùng được băm an toàn thông qua hàm băm **BCrypt** (`passlib.context.CryptContext(schemes=["bcrypt"])`), không bao giờ lưu trữ mật khẩu gốc dưới dạng plain-text.
2. **Access Token JWT:**
   - Ký bằng thuật toán `HS256` với khóa bí mật `JWT_SECRET_KEY`.
   - Chứa định danh người dùng trong trường chuẩn `sub`.
   - Có thời gian hiệu lực xác định (`ACCESS_TOKEN_EXPIRE_MINUTES`).
3. **Phân quyền hướng đối tượng (`RoleChecker`):**
   ```python
   # app/api/deps.py
   class RoleChecker:
       def __init__(self, allowed_roles: list[str]) -> None:
           self.allowed_roles = allowed_roles
       def __call__(self, current_user: User = Depends(get_current_user)) -> User:
           ...
   ```
   - Sử dụng đơn giản qua Dependency Injection: `@router.post("/roles", dependencies=[Depends(require_admin)])`.
   - Ngăn chặn triệt để tình trạng bypass từ phía client.

---

## 6. Hướng dẫn cài đặt & Khởi chạy Backend

### 6.1. Yêu cầu môi trường
- Python 3.11 hoặc 3.12.
- PostgreSQL hoặc SQLite.

### 6.2. Cấu hình biến môi trường (`.env`)
Tạo file `backend/.env`:
```dotenv
DATABASE_URL=sqlite:///./test.db
# Hoặc PostgreSQL:
# DATABASE_URL=postgresql+psycopg://app_user:password@localhost:5432/product_management

JWT_SECRET_KEY=super_secret_jwt_key_for_development_change_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 6.3. Cài đặt thư viện & Khởi chạy server
```powershell
# Di chuyển vào thư mục backend
cd backend

# Kích hoạt môi trường ảo (nếu có)
.\.venv\Scripts\Activate.ps1

# Cài đặt thư viện phụ thuộc
pip install -r requirements.txt

# Khởi chạy Uvicorn server
$env:PYTHONPATH = "src"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Tài liệu Swagger UI tương tác:** Truy cập tại [http://localhost:8000/docs](http://localhost:8000/docs)
- **Tài liệu ReDoc:** Truy cập tại [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 7. Kiểm thử tự động (Automated Testing)

Backend tích hợp đầy đủ bộ test unit và integration sử dụng **pytest** và **FastAPI TestClient** với in-memory SQLite database độc lập:

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/ -v
```
Toàn bộ các ca kiểm thử xác thực, đổi mật khẩu, phân quyền admin, tạo user và tạo role đều được kiểm tra nghiêm ngặt.
