# Product Management System (Product-Catalog)

Hệ thống ứng dụng web quản lý sản phẩm và danh mục toàn diện được xây dựng trên nền tảng **FastAPI (Python)**, **React 19 (Vite)**, **SQLAlchemy ORM**, xác thực bảo mật **JWT & BCrypt**, hệ thống phân quyền **RBAC (User / Admin / Custom Roles)** và cơ chế tự động hóa khởi tạo Database (Auto-migration & Data Bootstrapping).

> **Trạng thái dự án:** Đã hoàn thành toàn bộ các chức năng cốt lõi từ Backend (REST API, Authentication, RBAC, CRUD, Search, Filter, Sort, Pagination) đến Frontend (Storefront cho khách hàng, Admin Backoffice cho quản trị viên, Trang hồ sơ cá nhân và Quản lý Role).

---

## 1. Mục lục tài liệu

- 📖 **[Tài liệu Kỹ thuật Backend](file:///d:/Product-Catalog/backend/README.md):** Kiến trúc phân tầng 3 lớp, ORM Models, DTO Schemas, Repositories, Services, Security, API Endpoints và Hướng dẫn test.
- 🎨 **[Tài liệu Kỹ thuật Frontend](file:///d:/Product-Catalog/frontend/README.md):** Kiến trúc React 19, Component Hierarchy, Dual-flow (Storefront & Admin), Profile View, Font Awesome icons, API Client.
- 📑 **[Báo Cáo Tổng Hợp Toàn Bộ Hệ Thống](file:///d:/Product-Catalog/TONG_HOP_HE_THONG.md):** Bảng tóm tắt tổng quan ngắn gọn chi tiết về toàn bộ giải pháp từ A-Z.
- 📅 **[Nhật Ký Tiến Độ Công Việc](file:///d:/Product-Catalog/BAO_CAO_CONG_VIEC.md):** Ghi nhận quá trình triển khai chi tiết qua từng mốc phát triển.

---

## 2. Công nghệ sử dụng

| Phân hệ | Công nghệ | Chi tiết sử dụng |
|---|---|---|
| **Backend** | Python 3.11+, FastAPI | RESTful API Framework hiệu năng cao, ASGI |
| **ORM & Database** | SQLAlchemy 2.0, SQLite / PostgreSQL | Declarative Models, connection pool với `pool_pre_ping=True` |
| **Data Validation** | Pydantic v2, pydantic-settings | Data Transfer Objects (DTOs), Generic Paginated Schema, Settings |
| **Authentication & RBAC**| PyJWT, Passlib (BCrypt) | Mã hóa mật khẩu an toàn, JWT Bearer Token, `RoleChecker` OOP guard |
| **Database Bootstrap** | Custom auto-migration (`init_db.py`) | Tự nâng cấp schema `password_hash`, idempotent seed roles & super admin |
| **Frontend** | React 19, Vite | Single Page Application (SPA), React Hooks |
| **UI & Icons** | Dark Theme CSS, Font Awesome 6.5.2 | Giao diện hiện đại, responsive, bộ icon nhận diện trực quan |
| **HTTP Communication** | Native Fetch API Wrapper + Vite Proxy | Proxy chuyển tiếp `/Thuancyber` sang backend cổng 8000 |
| **Testing** | Pytest, FastAPI TestClient | In-memory SQLite testing cho toàn bộ auth, roles, CRUD |

---

## 3. Kiến trúc tổng thể hệ thống

```text
               TRÌNH DUYỆT NGƯỜI DÙNG (Browser)
                              │
     ┌────────────────────────┴────────────────────────┐
     ▼                                                 ▼
[Storefront View]                              [Admin Backoffice]
- Xem danh mục & sản phẩm                      - Route Guard (Admin only)
- Hero Search & Category Chips                 - Quản lý Sản phẩm (CRUD, Filter)
- Giỏ hàng & Xem chi tiết                      - Quản lý Danh mục (CRUD)
                                               - Quản lý User & Role Management
                                               - Live API Logger
     │                                                 │
     └────────────────────────┬────────────────────────┘
                              ▼ (HTTP / JSON)
                     [Vite Reverse Proxy]
                      Port: 5173 (/Thuancyber)
                              │
                              ▼
           ┌────────────────────────────────────────┐
           │      FastAPI Backend (Port: 8000)      │
           │                                        │
           │  ├── Routers (/Thuancyber/*)           │
           │  ├── Dependencies & RBAC Guards        │
           │  ├── Service Layer (Business Logic)    │
           │  ├── Repository Layer (Generic OOP)    │
           │  └── Auto-Bootstrap (init_db.py)       │
           └──────────────────┬─────────────────────┘
                              │ (SQLAlchemy ORM)
                              ▼
           ┌────────────────────────────────────────┐
           │          Database Storage              │
           │  - roles (admin, user, custom roles)   │
           │  - users (BCrypt password hash)        │
           │  - categories (name, description)      │
           │  - products (price, stock, category_id)│
           └────────────────────────────────────────┘
```

---

## 4. Cấu trúc thư mục dự án

```text
Product-Catalog/
├── README.md                           # Tài liệu tổng quan dự án (File này)
├── TONG_HOP_HE_THONG.md                # Báo cáo tổng hợp ngắn gọn chi tiết toàn hệ thống
├── BAO_CAO_CONG_VIEC.md                # Nhật ký tiến độ công việc hàng ngày
├── backend/                            # Phân hệ Backend (FastAPI)
│   ├── README.md                       # Tài liệu hướng dẫn kỹ thuật Backend
│   ├── requirements.txt                # Thư viện phụ thuộc Python
│   ├── tests/                          # Bộ kiểm thử tích hợp (pytest)
│   │   ├── test_auth_endpoints.py      # Test xác thực, đổi mật khẩu, phân quyền, role
│   │   └── test_products_categories.py # Test CRUD sản phẩm và danh mục
│   └── src/
│       └── app/
│           ├── main.py                 # FastAPI app, CORS, mount routers
│           ├── api/deps.py             # get_db, JWT auth & RoleChecker
│           ├── core/                   # Cấu hình, database, security, init_db
│           ├── models/                 # SQLAlchemy models (User, Role, Category, Product)
│           ├── schemas/                # Pydantic schemas (Auth, Category, Product, Pagination)
│           ├── repositories/           # Repositories (Base Generic, Role, User, Category, Product)
│           ├── services/               # Services (CategoryService, ProductService)
│           └── routers/                # Routers (auth, users, categories, products)
└── frontend/                           # Phân hệ Frontend (React 19 Feature-Based Architecture)
    ├── README.md                       # Tài liệu hướng dẫn kỹ thuật Frontend
    ├── package.json                    # Cấu hình dự án Frontend
    ├── vite.config.js                  # Vite dev server & proxy cấu hình /Thuancyber
    ├── index.html                      # HTML root, CDN Font Awesome 6.5.2
    └── src/
        ├── app/                        # App.jsx, router.jsx, providers.jsx
        ├── api/                        # client.js, endpoints.js, errorHandler.js
        ├── layouts/                    # MainLayout.jsx, AdminLayout.jsx, AuthLayout.jsx
        ├── features/                   # auth, products, categories, users, profile
        ├── components/                 # common/ (Button, Input, Modal...), navigation/ (Navbar, Sidebar...)
        ├── guards/                     # AuthGuard.jsx, RoleGuard.jsx
        ├── hooks/                      # useDebounce.js
        ├── utils/                      # formatCurrency.js, validators.js
        ├── styles/                     # variables.css, global.css, layout.css, components.css
        └── main.jsx                    # Entry point React 19 root
```

---

## 5. Danh mục RESTful API (Prefix: `/Thuancyber`)

Tất cả các API được bảo vệ và định tuyến qua tiền tố `/Thuancyber`:

### 5.1. Authentication & Cá nhân (`/Thuancyber/auth`)
- `POST /Thuancyber/auth/register`: Đăng ký tài khoản mới (vai trò mặc định `user`).
- `POST /Thuancyber/auth/login`: Đăng nhập, nhận JWT Access Token.
- `GET /Thuancyber/auth/me`: Lấy thông tin tài khoản đang đăng nhập.
- `PATCH /Thuancyber/auth/me`: Cập nhật họ tên hiển thị.
- `POST /Thuancyber/auth/change-password`: Đổi mật khẩu cá nhân.

### 5.2. Quản lý Người dùng & Phân quyền Vai trò (`/Thuancyber/users`)
- `GET /Thuancyber/users`: Lấy danh sách toàn bộ người dùng (Yêu cầu `Admin`).
- `POST /Thuancyber/users`: Admin tạo người dùng mới và phân vai trò trực tiếp (Yêu cầu `Admin`).
- `PATCH /Thuancyber/users/{id}/status`: Khóa hoặc mở khóa tài khoản (Yêu cầu `Admin`).
- `PATCH /Thuancyber/users/{id}/role`: Thay đổi vai trò người dùng (Yêu cầu `Admin`).
- `GET /Thuancyber/users/roles`: Lấy danh sách tất cả các vai trò trong hệ thống.
- `POST /Thuancyber/users/roles`: **Thêm vai trò mới** động (ví dụ `manager`, `editor`, `staff`...) (Yêu cầu `Admin`).

### 5.3. Quản lý Danh mục Sản phẩm (`/Thuancyber/categories`)
- `GET /Thuancyber/categories`: Lấy danh sách danh mục (Công khai).
- `GET /Thuancyber/categories/{id}`: Xem chi tiết danh mục (Công khai).
- `POST /Thuancyber/categories`: Tạo mới danh mục (Yêu cầu `Admin`).
- `PUT /Thuancyber/categories/{id}`: Cập nhật danh mục (Yêu cầu `Admin`).
- `DELETE /Thuancyber/categories/{id}`: Xóa danh mục (Yêu cầu `Admin`, tự động chặn nếu đang có sản phẩm).

### 5.4. Quản lý Sản phẩm (`/Thuancyber/products`)
- `GET /Thuancyber/products`: Lấy danh sách sản phẩm (Công khai, hỗ trợ lọc đa điều kiện):
  - `page`, `page_size`: Phân trang dữ liệu.
  - `search`: Tìm kiếm gần đúng theo tên (`ilike`).
  - `category_id`: Lọc theo danh mục.
  - `min_price`, `max_price`: Lọc theo khoảng giá.
  - `sort_by`, `order`: Sắp xếp an toàn theo whitelist (`price`, `created_at`, `name`, `id`).
- `GET /Thuancyber/products/{id}`: Xem chi tiết sản phẩm theo ID (Công khai).
- `POST /Thuancyber/products`: Thêm mới sản phẩm (Yêu cầu `Admin`).
- `PUT /Thuancyber/products/{id}`: Cập nhật toàn bộ sản phẩm (Yêu cầu `Admin`).
- `PATCH /Thuancyber/products/{id}`: Cập nhật từng trường sản phẩm (Yêu cầu `Admin`).
- `DELETE /Thuancyber/products/{id}`: Xóa sản phẩm (Yêu cầu `Admin`).

---

## 6. Hướng dẫn Khởi chạy Hệ thống

### 6.1. Khởi chạy Backend (Cổng 8000)
Mở một cửa sổ Terminal tại thư mục `backend`:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1   # (Nếu có virtual environment)
pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* Tài liệu Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### 6.2. Khởi chạy Frontend (Cổng 5173)
Mở một cửa sổ Terminal thứ hai tại thư mục `frontend`:
```bash
cd frontend
npm install
npm run dev
```
* Ứng dụng Web: [http://localhost:5173](http://localhost:5173)

---

## 7. Tài khoản kiểm thử có sẵn (Mặc định tự sinh)

Hệ thống tự động kích hoạt cơ chế Bootstrap nạp sẵn tài khoản Super Admin khi khởi động máy chủ:
- **Tài khoản Quản trị viên (Admin):**
  - **Email:** `admin@system.local`
  - **Mật khẩu:** `Admin@123456`
  - **Vai trò:** `admin` (Có toàn quyền truy cập Trang Admin, Quản lý sản phẩm, danh mục, người dùng và thêm vai trò mới).
- **Tài khoản Người dùng thông thường (Khách hàng):**
  - Bấm nút **"Đăng ký"** trên giao diện để tự tạo tài khoản mới ngay lập tức (mặc định vai trò `user`).
