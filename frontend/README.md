# Frontend — Product Management Web Application

Giao diện người dùng hiện đại, tốc độ cao được xây dựng trên nền tảng **React 19**, **Vite**, bộ icon chuẩn **Font Awesome 6.5.2**, thiết kế hỗ trợ Responsive và phân tách hoàn toàn 2 luồng trải nghiệm người dùng (**Storefront** dành cho khách hàng & **Admin Backoffice** dành cho quản trị viên).

---

## 1. Điểm nổi bật về kiến trúc & Trải nghiệm người dùng

1. **Phân tách 2 luồng độc lập (Dual User Flow):**
   - **Luồng Khách hàng (Customer Storefront):** Giao diện mua sắm trực quan, tìm kiếm thông minh dạng Hero search, lọc theo danh mục dạng Chips, xem chi tiết sản phẩm và giỏ hàng mô phỏng.
   - **Luồng Quản trị (Admin Backoffice):** Khu vực quản lý toàn diện chỉ hiển thị khi tài khoản đăng nhập có quyền `admin`. Tích hợp route guard ngăn chặn truy cập trái phép.
2. **Quản lý Vai trò & Phân quyền động (Role Management):**
   - Cho phép Admin xem danh sách tất cả các vai trò, mô tả và số lượng người dùng đang giữ vai trò đó.
   - Hỗ trợ tạo mới vai trò trực tiếp (như `manager`, `editor`, `staff`, `moderator`...).
   - Tự động đồng bộ vai trò mới tạo vào dropdown khi thêm tài khoản hoặc đổi quyền người dùng.
3. **Trang Cá Nhân (Profile View):**
   - Xem thông tin hồ sơ tài khoản (Email, họ tên, vai trò, ngày tạo).
   - Đổi họ tên hiển thị cá nhân (`PATCH /Thuancyber/auth/me`).
   - Đổi mật khẩu an toàn (`POST /Thuancyber/auth/change-password`).
4. **Bảo mật & Trải nghiệm đăng nhập tinh giản:**
   - Ẩn hoàn toàn thông tin mẫu tự động điền trong modal đăng nhập/đăng ký để đảm bảo tính thực tế và chuyên nghiệp.
   - Tự động lưu và gửi JWT Bearer token qua `localStorage`.
5. **Giám sát thời gian thực (Live API Logger):**
   - Tab giám sát dành riêng cho Admin hiển thị toàn bộ lịch sử các request/response HTTP gửi đến Backend kèm mã trạng thái (200, 201, 401, 403, 404, 409...) và thời gian phản hồi.

---

## 2. Cấu trúc thư mục & Component Hierarchy

```text
frontend/
├── public/
├── src/
│   ├── app/
│   │   ├── App.jsx
│   │   ├── router.jsx
│   │   └── providers.jsx
│   │
│   ├── assets/
│   │   ├── images/
│   │   └── icons/
│   │
│   ├── api/
│   │   ├── client.js
│   │   ├── endpoints.js
│   │   └── errorHandler.js
│   │
│   ├── layouts/
│   │   ├── MainLayout.jsx
│   │   ├── AdminLayout.jsx
│   │   └── AuthLayout.jsx
│   │
│   ├── features/
│   │   ├── auth/
│   │   │   ├── components/ (LoginForm, RegisterForm, AuthModal)
│   │   │   ├── services/ (authService.js)
│   │   │   ├── hooks/ (useAuth.js)
│   │   │   └── utils/ (token.js)
│   │   │
│   │   ├── products/
│   │   │   ├── components/ (ProductList, ProductCard, ProductForm, ProductFilters, ProductPagination)
│   │   │   ├── services/ (productService.js)
│   │   │   ├── hooks/ (useProducts.js)
│   │   │   └── pages/ (ProductsPage.jsx)
│   │   │
│   │   ├── categories/
│   │   │   ├── components/ (CategoryList, CategoryForm)
│   │   │   ├── services/ (categoryService.js)
│   │   │   └── pages/ (CategoriesPage.jsx)
│   │   │
│   │   ├── users/
│   │   │   ├── components/ (UserList, UserForm, RoleSelector)
│   │   │   ├── services/ (userService.js)
│   │   │   └── pages/ (UsersPage.jsx)
│   │   │
│   │   └── profile/
│   │       ├── components/ (ProfileForm, ChangePasswordForm)
│   │       ├── services/ (profileService.js)
│   │       └── pages/ (ProfilePage.jsx)
│   │
│   ├── components/
│   │   ├── common/ (Button, Input, Modal, ConfirmDialog, Loading, ErrorMessage)
│   │   └── navigation/ (Navbar, Sidebar, Breadcrumbs)
│   │
│   ├── hooks/ (useDebounce.js)
│   ├── guards/ (AuthGuard.jsx, RoleGuard.jsx)
│   ├── utils/ (formatCurrency.js, validators.js)
│   ├── styles/ (variables.css, global.css, layout.css, components.css)
│   ├── main.jsx
│   └── index.css
│
├── .env.local
├── .gitignore
├── package.json
├── vite.config.js
└── index.html
```

---

## 3. Chi tiết các chức năng giao diện

### 3.1. Cửa hàng mua sắm (Storefront View)
- **Hero Search Box:** Thanh tìm kiếm sản phẩm nhanh nổi bật ngay đầu trang.
- **Category Chips Bar:** Thanh chọn danh mục nhanh dạng nút chip trượt ngang, tự động lọc sản phẩm khi click.
- **Product Cards Grid:** Danh sách sản phẩm dạng thẻ với:
  - Tên sản phẩm, mô tả tóm tắt, huy hiệu danh mục.
  - Giá tiền định dạng VND chuẩn (`toLocaleString('vi-VN')`).
  - Trạng thái tồn kho còn hàng / hết hàng.
  - Nút "Chọn mua" (thêm vào giỏ hàng) và nút "Xem chi tiết".
- **Modal Chi Tiết Sản Phẩm:** Hiển thị thông số đầy đủ, ngày tạo, cập nhật và mô tả chi tiết.
- **Giỏ Hàng Mô Phỏng (Shopping Cart Modal):**
  - Xem danh sách món hàng đã chọn, tùy chỉnh tăng/giảm số lượng hoặc xóa khỏi giỏ.
  - Tự động tính tổng tiền thanh toán.
  - Nút "Thanh toán" mô phỏng quy trình đặt hàng hoàn tất.

---

### 3.2. Trung tâm Quản trị (Admin Backoffice)
Khu vực này được bảo vệ bởi Route Guard:
- Khách chưa đăng nhập hoặc người dùng thường có role `user` khi cố tình mở view này sẽ nhận thông báo **403 Forbidden** và nút chuyển về Cửa hàng.
- Nút "Trang Admin" trên Navbar chính chỉ xuất hiện khi tài khoản đăng nhập có `role_name === 'admin'`.

Bên trong Admin Backoffice gồm 4 tab điều hướng:
1. **Quản lý Sản phẩm (`ProductSection`):**
   - Bảng sản phẩm đầy đủ phân trang, lọc theo danh mục, khoảng giá `min_price` - `max_price` và tìm kiếm tên sản phẩm.
   - Sắp xếp cột an toàn (theo giá, tên, ngày tạo).
   - Form Thêm mới / Cập nhật sản phẩm với đầy đủ ràng buộc validation.
   - Xóa sản phẩm với hộp thoại xác nhận an toàn.
2. **Quản lý Danh mục (`CategorySection`):**
   - Danh sách các nhóm danh mục hiện có trong hệ thống.
   - Form thêm mới danh mục (kiểm tra không trùng lặp).
   - Chỉnh sửa thông tin danh mục.
   - Xóa danh mục (Backend tự động chặn nếu còn sản phẩm thuộc danh mục đó).
3. **Quản lý Người dùng & Vai trò (`UserManagement`):**
   - **Bảng người dùng:** Hiển thị ID, Họ tên, Email, Vai trò, Trạng thái (Hoạt động / Bị khóa), Ngày đăng ký.
   - **Khóa / Mở khóa tài khoản:** Nút thao tác một chạm nhanh chóng (Admin không thể tự khóa tài khoản của chính mình).
   - **Đổi vai trò người dùng:** Modal chọn vai trò mới từ danh sách roles khả dụng.
   - **Thêm người dùng mới:** Admin tạo trực tiếp tài khoản mới và chọn vai trò khởi tạo.
   - **Quản lý & Thêm Vai Trò Mới (Role Management):**
     - Khối thông tin tổng quan các vai trò trong hệ thống kèm số lượng tài khoản thuộc vai trò.
     - Modal tạo vai trò mới (Tên mã vai trò chuẩn hóa chữ thường, mô tả trách nhiệm).
     - Tự động cập nhật vào các dropdown chọn vai trò trên toàn hệ thống.
4. **Nhật ký API Backend (`ApiLogger`):**
   - Theo dõi từng cuộc gọi mạng gửi đến Backend.
   - Ghi nhận Method (GET, POST, PUT, PATCH, DELETE), URL, Response Status và mã màu trực quan (xanh lá cho 200/201, vàng cho 400, đỏ cho 401/403).

---

### 3.3. Trang Cá Nhân (Profile View)
- Xem thông tin hồ sơ chi tiết: Email, Họ và tên, Vai trò hiện tại, Trạng thái kích hoạt và Ngày đăng ký.
- Cập nhật Họ và Tên: Gửi request `PATCH /Thuancyber/auth/me`.
- Đổi Mật Khẩu Cá Nhân: Nhập mật khẩu hiện tại và mật khẩu mới (tối thiểu 6 ký tự), gửi request `POST /Thuancyber/auth/change-password`.

---

## 4. Giao tiếp API & Cấu hình Reverse Proxy

Thay vì dùng thư viện bên ngoài cồng kềnh, Frontend sử dụng module HTTP Client thuần túy đóng gói trong [src/api/client.js](file:///d:/Product-Catalog/frontend/src/api/client.js):
- Tự động đính kèm Header `Authorization: Bearer <token>` nếu người dùng đã đăng nhập.
- Tự động phân tích JSON và bắt lỗi HTTP từ Backend để hiển thị Toast thông báo.
- Gửi sự kiện cập nhật trực tiếp sang `ApiLogger`.

Cấu hình Reverse Proxy trong [vite.config.js](file:///d:/Product-Catalog/frontend/vite.config.js):
```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/Thuancyber': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```
Mọi request từ Frontend gọi tới `/Thuancyber/*` đều được tự động chuyển tiếp an toàn tới Backend chạy tại cổng `8000`, loại bỏ hoàn toàn các trở ngại về CORS trong môi trường phát triển.

---

## 5. Hướng dẫn cài đặt & Khởi chạy Frontend

### 5.1. Yêu cầu môi trường
- Node.js phiên bản 18+ hoặc 20+ LTS.
- Trình quản lý gói `npm`.

### 5.2. Cài đặt và Chạy máy chủ phát triển
```bash
# Di chuyển vào thư mục frontend
cd frontend

# Cài đặt các gói phụ thuộc
npm install

# Khởi chạy Vite Dev Server
npm run dev
```

Sau khi chạy lệnh trên, ứng dụng sẽ hoạt động tại:
👉 **[http://localhost:5173](http://localhost:5173)**

---

## 6. Bộ biểu tượng Font Awesome

Hệ thống sử dụng bộ icon chuẩn **Font Awesome 6.5.2** thông qua liên kết CDN trong `index.html`:
- `<i className="fa-solid fa-store"></i>`: Cửa hàng.
- `<i className="fa-solid fa-shield-halved"></i>`: Admin & Quyền quản trị.
- `<i className="fa-solid fa-user-plus"></i>`: Thêm tài khoản người dùng.
- `<i className="fa-solid fa-shield-plus"></i>`: Thêm vai trò mới.
- `<i className="fa-solid fa-lock"></i>` / `fa-lock-open`: Khóa / Mở khóa tài khoản.
- `<i className="fa-solid fa-cart-shopping"></i>`: Giỏ hàng.
- `<i className="fa-solid fa-boxes-stacked"></i>`: Danh mục sản phẩm.
