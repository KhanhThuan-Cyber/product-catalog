# Backend — Product Catalog API Documentation

Tài liệu kỹ thuật chuyên sâu về phân hệ Backend RESTful API của hệ thống **Product Catalog**, được xây dựng trên nền tảng **FastAPI (Python 3.12)**, **SQLAlchemy ORM 2.0**, **Pydantic v2**, **Redis 7** và **PostgreSQL 16**.

---

## 1. Kiến trúc Phân tầng 3 Lớp (Layered Architecture)

Hệ thống tuân thủ nghiêm ngặt nguyên lý Single Responsibility (SRP) và mô hình phân tầng tiêu chuẩn doanh nghiệp:

```text
HTTP Request (Client / Browser / Swagger)
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│ 1. API & ROUTER TIER (FastAPI Routers)                 │
│    - routers/products.py, categories.py, auth.py, ...  │
│    - Xử lý tham số Query, Path, Body                   │
│    - Dependency Injection: get_db, RoleChecker         │
│    - Xác thực DTOs đầu vào qua Pydantic v2             │
└───────────────────────┬────────────────────────────────┘
                        │ Data Transfer Objects (DTOs)
                        ▼
┌────────────────────────────────────────────────────────┐
│ 2. SERVICE TIER (Business Logic & Cache Coordination)  │
│    - services/product_service.py, category_service.py  │
│    - Điều phối Cache-Aside: Kiểm tra RAM Redis         │
│    - Quản lý Transaction (Commit / Rollback)           │
│    - Invalidate cache khi có thao tác Create/Update/Del│
└───────────────────────┬────────────────────────────────┘
                        │ Domain Entities & Query Filters
                        ▼
┌────────────────────────────────────────────────────────┐
│ 3. REPOSITORY TIER (Data Access Layer)                 │
│    - repositories/product_repository.py, base_repo.py  │
│    - Áp dụng BaseFilter (ILIKE search, price range)   │
│    - Whitelist sort chống SQL Injection               │
│    - Generic Pagination query execution                │
└───────────────────────┬────────────────────────────────┘
                        │ SQLAlchemy ORM Mapped Models
                        ▼
┌────────────────────────────────────────────────────────┐
│ 4. DATABASE & INFRASTRUCTURE TIER                      │
│    - models/product.py, category.py, user.py, role.py  │
│    - Redis 7 (In-Memory Cache & JTI Blacklist)         │
│    - PostgreSQL 16 (Relational Persistent Storage)     │
└────────────────────────────────────────────────────────┘
```

---

## 2. Cấu trúc Thư mục Chi tiết

```text
backend/
├── Dockerfile                      # Image container python:3.12-slim
├── requirements.txt                # Thư viện phụ thuộc
├── alembic.ini                     # Cấu hình công cụ di chuyển dữ liệu Alembic
├── alembic/                        # Các bản ghi migration cơ sở dữ liệu
│   ├── env.py                      # Cấu hình kết nối DB và Base.metadata
│   └── versions/                   # Lịch sử các file migration (.py)
├── run-tests.ps1                   # Script thực thi toàn bộ 63 kiểm thử Pytest
├── tests/                          # Bộ kiểm thử tự động
│   ├── conftest.py                 # Fixture test, mock redis & in-memory sqlite
│   ├── test_auth_endpoints.py      # Test đăng ký, đăng nhập, đổi mật khẩu
│   ├── test_auth_blacklist.py      # Test JTI token blacklist khi logout
│   ├── test_product_cache.py       # Test Cache Hit, Cache Miss, Invalidation
│   ├── test_category_cache.py      # Test cache danh mục
│   ├── test_product_filter.py      # Test bộ lọc, khoảng giá, whitelist sort
│   ├── test_rate_limit.py          # Test Fixed-Window Rate Limiter
│   └── test_pagination_schema.py   # Test schema PaginatedResponse generic
└── src/app/
    ├── main.py                     # Entry point FastAPI, CORS, mount routers
    ├── api/
    │   └── deps.py                 # Dependency: get_db, get_current_user, RoleChecker
    ├── core/
    │   ├── config.py               # Pydantic Settings đọc cấu hình từ .env
    │   ├── database.py             # Engine SQLAlchemy, SessionLocal, pool_pre_ping
    │   ├── redis.py                # Redis client singleton & NoOp graceful degradation
    │   ├── rate_limiter.py         # Bộ giới hạn tần suất request theo IP qua Redis
    │   ├── security.py             # BCrypt hashing, JWT encode/decode, token rotation
    │   ├── init_db.py              # Tự động hóa tạo bảng, seed role & admin mặc định
    │   └── seed.py                 # Hàm sinh 120 sản phẩm mẫu (idempotent)
    ├── models/                     # Declarative ORM Models
    │   ├── base.py                 # Base declarative
    │   ├── role.py                 # Bảng roles (admin, user, custom)
    │   ├── user.py                 # Bảng users (email, password_hash, role_id)
    │   ├── category.py             # Bảng categories (name unique, description)
    │   └── product.py              # Bảng products (price, stock, category_id FK)
    ├── schemas/                    # Pydantic v2 DTOs
    │   ├── auth.py                 # Schemas cho xác thực, login, register, token
    │   ├── pagination.py           # PaginatedResponse[T], PaginationParams
    │   ├── product_filter.py       # ProductFilter (validate min_price <= max_price)
    │   ├── sorting.py              # ProductSortBy, SortOrder Enums
    │   ├── category.py             # CategoryCreate, CategoryUpdate, CategoryResponse
    │   └── product.py              # ProductCreate, ProductUpdate, ProductPatch, ProductResponse
    ├── repositories/               # Tầng truy vấn dữ liệu ORM
    │   ├── base_repository.py      # Repository trừu tượng hỗ trợ generic paginate
    │   ├── base_filter.py          # Logic áp dụng search ilike, range, safe sort
    │   ├── category_repository.py  # Query Category (get_by_name, delete)
    │   └── product_repository.py   # Query Product (lọc theo filter_params, paginate)
    └── services/                   # Tầng xử lý nghiệp vụ & cache
        ├── base.py                 # BaseService hỗ trợ commit/rollback an toàn
        ├── cache_service.py        # Quản lý đọc/ghi/xóa cache Redis qua SCAN pipeline
        ├── auth_service.py         # Nghiệp vụ xác thực, token blacklist, rate limit
        ├── category_service.py     # Ràng buộc khóa ngoại khi xóa danh mục
        └── product_service.py      # CRUD sản phẩm kết hợp Cache-Aside
```

---

## 3. Cơ chế Caching & Phòng vệ sập nguồn (Redis & Graceful Fallback)

### A. Chiến lược Cache-Aside (Lazy Loading)
- **Đọc danh sách sản phẩm (`GET /products`):**
  - Tham số query (`page`, `page_size`, `search`, `category_id`, `min_price`, `max_price`, `sort_by`, `order`) được lọc bỏ `None`, sắp xếp key tăng dần và băm MD5 để tạo key tất định dạng: `product:list:<md5_hash>`.
  - Nếu có trong Redis $\rightarrow$ Trả về dữ liệu ngay lập tức (**Cache HIT**).
  - Nếu không có $\rightarrow$ Truy vấn PostgreSQL $\rightarrow$ Ghi vào Redis với TTL $\rightarrow$ Trả về Client (**Cache MISS**).
- **Đọc chi tiết sản phẩm (`GET /products/{id}`):**
  - Cache theo key `product:detail:{id}` với TTL tương ứng.
- **Xóa Cache (Invalidation):**
  - Khi có thao tác Tạo / Sửa / Xóa sản phẩm: Hệ thống gọi `cache_service.invalidate_product_caches(product_id)`.
  - Thay vì dùng lệnh `KEYS *` gây treo toàn bộ cụm Redis, service sử dụng lệnh `SCAN` kết hợp `pipeline.delete` để xóa an toàn theo từng khối (batch 100 keys).

### B. Graceful Degradation (Phục hồi an toàn)
Trong module [`core/redis.py`](file:///d:/Product-Catalog/backend/src/app/core/redis.py), nếu Redis không phản hồi hoặc bị sập, một instance `NoOpRedisClient` sẽ được sử dụng thay thế. Mọi lệnh `get()` trả về `None` (coi như Cache Miss) và hệ thống chuyển thẳng truy vấn xuống PostgreSQL, giúp ứng dụng không bao giờ bị dừng hoạt động.

---

## 4. Xác thực & Bảo mật (JWT, RTR, JTI Blacklist, Rate Limiting)

1. **Băm mật khẩu:** Sử dụng **BCrypt** với chuỗi Salt ngẫu nhiên và Work factor tiêu chuẩn, chống lại các cuộc tấn công Rainbow Table.
2. **Access Token & Refresh Token:**
   - Access Token có thời hạn 30 phút, chứa trường `jti` (JWT ID dạng UUID4).
   - Refresh Token có thời hạn 7 ngày, áp dụng cơ chế **Refresh Token Rotation (RTR)**: Mỗi lần xin cấp lại Access Token mới, Refresh Token cũ sẽ bị hủy và thay bằng token mới.
3. **Đăng xuất an toàn (JTI Blacklist):**
   - Khi gọi `POST /auth/logout`, backend đọc `jti` từ token, tính toán thời gian sống còn lại (`TTL = exp - now`) và ghi vào Redis dạng: `blacklist:{jti}`.
   - Dependency `get_current_user` sẽ từ chối ngay lập tức bất kỳ token nào có `jti` nằm trong danh sách đen này.
4. **Giới hạn tần suất (Fixed-Window Rate Limiting):**
   - Áp dụng trên các endpoint nhạy cảm như `/auth/login` (tối đa 10 lần / 15 phút) và `/auth/register` (tối đa 5 lần / 1 giờ) dựa trên địa chỉ IP của Client thông qua Redis key có TTL.

---

## 5. Hướng dẫn Khởi chạy & Kiểm thử Backend

### Khởi chạy môi trường Dev:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "src"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### Chạy bộ kiểm thử tự động (Pytest):
Backend trang bị sẵn script PowerShell thực thi độc lập toàn bộ 63 test cases:
```powershell
cd backend
.\run-tests.ps1
```
Script sẽ tự động nạp `PYTHONPATH=src` và chạy pytest với báo cáo chi tiết từng ca kiểm thử.
