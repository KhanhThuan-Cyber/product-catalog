# Frontend — Product Catalog Web Application

Tài liệu kỹ thuật chuyên sâu về phân hệ Frontend của hệ thống **Product Catalog**, được xây dựng trên nền tảng **React 19**, công cụ đóng gói siêu tốc **Vite**, bộ icon **Font Awesome 6.5.2** và thiết kế tối ưu hóa trải nghiệm người dùng kép (**Dual User Flow**).

---

## 1. Điểm nổi bật về Kiến trúc & Trải nghiệm

1. **Phân tách 2 luồng trải nghiệm độc lập (Dual User Flow):**
   - **Storefront View (Dành cho Khách hàng):** Giao diện dạng lưới thẻ hiện đại (Card Grid), tìm kiếm sản phẩm thông minh, lọc danh mục dạng thẻ bấm (Category Chips), xem chi tiết qua Modal tương tác và giỏ hàng mô phỏng.
   - **Admin Backoffice (Dành cho Quản trị viên):** Bảng dữ liệu quản lý toàn diện (Data Table) tích hợp chức năng sửa nhanh Giá bán và Số lượng tồn kho (Quick-Patch), quản lý Danh mục, phân quyền Người dùng và tạo Vai trò động.
2. **Kiến trúc Feature-Based (Tổ chức theo Tính năng):**
   - Thay vì gom chung toàn bộ components và hooks vào một thư mục lớn, mã nguồn chia tách thành các module nghiệp vụ độc lập (`features/products`, `features/categories`, `features/auth`, `features/users`, `features/profile`).
3. **Cơ chế Giám sát Thời gian thực (Live API Logger):**
   - Tích hợp sẵn bảng điều khiển theo dõi mạng nội bộ (Internal Network Monitor) cho Admin, hiển thị trực quan mọi HTTP Request gửi đi từ giao diện, mã trạng thái HTTP (200, 201, 401, 403, 404, 409) và thời gian phản hồi theo thời gian thực thông qua mẫu thiết kế Pub/Sub.
4. **Bảo vệ Tuyến đường Đa tầng (Client Route Guards):**
   - Tích hợp `AuthGuard` và `RoleGuard` tự động kiểm tra trạng thái đăng nhập và vai trò người dùng trong LocalStorage, chủ động chuyển hướng (Redirect) về trang an toàn nếu người dùng cố ý truy cập trái phép.

---

## 2. Cấu trúc Thư mục Frontend

```text
frontend/
├── Dockerfile                  # Multi-stage build (Node 20 Alpine -> Nginx Alpine)
├── nginx.conf                  # Cấu hình Nginx reverse proxy, Gzip compression, SPA fallback
├── package.json                # React 19, Axios, Vite
├── vite.config.js              # Cấu hình dev server & reverse proxy
├── index.html                  # File HTML gốc tích hợp Font Awesome 6.5.2
└── src/
    ├── main.jsx                # Entry point gắn kết React vào DOM
    ├── app/
    │   ├── App.jsx             # Component điều phối chính (Storefront & Admin)
    │   ├── router.jsx          # Custom lightweight hash router (#store, #admin, #profile)
    │   └── providers.jsx       # Context providers cho Giỏ hàng (Cart) và Thông báo (Toast)
    ├── api/                    # Tầng giao tiếp HTTP Client
    │   ├── client.js           # Cấu hình Axios instance, request interceptor inject token & API logger pub/sub
    │   ├── endpoints.js        # Khai báo tập trung danh sách URL endpoints
    │   └── errorHandler.js     # Chuẩn hóa thông báo lỗi từ Backend
    ├── features/               # Các module tính năng độc lập
    │   ├── auth/               # Đăng nhập, Đăng ký, Quản lý Token, AuthModal
    │   ├── products/           # Danh sách sản phẩm, bộ lọc, phân trang, form thêm/sửa, Quick-Patch
    │   ├── categories/         # Quản lý danh mục sản phẩm (CRUD danh mục)
    │   ├── users/              # Quản lý danh sách tài khoản, khóa/mở khóa, tạo vai trò mới
    │   └── profile/            # Xem thông tin tài khoản, đổi họ tên, đổi mật khẩu
    ├── layouts/                # Khung giao diện (MainLayout, AdminLayout)
    ├── components/             # Components dùng chung (Button, Input, Modal, ConfirmDialog, Loading)
    ├── hooks/                  # Custom hooks (useDebounce, useProducts)
    ├── guards/                 # Bảo vệ route (AuthGuard, RoleGuard)
    ├── utils/                  # Tiện ích định dạng tiền tệ (formatCurrency) & validate form (validators)
    └── styles/                 # Hệ thống CSS module hóa (variables.css, global.css, components.css)
```

---

## 3. Quản lý State & Giao tiếp HTTP (Axios Architecture)

### A. Interceptor tự động gắn Bearer Token
Trong file [`api/client.js`](file:///d:/Product-Catalog/frontend/src/api/client.js), mọi request gửi đi đều được đi qua interceptor:
- Tự động đọc Access Token từ `localStorage` và nhúng vào Header:
  `Authorization: Bearer <access_token>`
- Tự động làm sạch các tham số query trống (`null`, `undefined`, chuỗi rỗng `""`) để tránh làm phân mảnh cache key trên Redis.
- Kích hoạt sự kiện phát sóng (Broadcast) đến component `ApiLogger` để hiển thị trên giao diện quản trị viên.

### B. Custom Hook `useProducts`
Hook quản lý toàn bộ vòng đời nạp dữ liệu sản phẩm, đóng gói:
- State dữ liệu: `products`, `total`, `totalPages`, `loading`, `error`.
- State bộ lọc: `page`, `pageSize`, `search`, `categoryId`, `minPrice`, `maxPrice`, `sortBy`, `order`.
- Hàm hỗ trợ: `setPage()`, `resetFilters()`, `refetch()`.

---

## 4. Đóng gói Production & Triển khai Nginx (Docker Multi-stage)

File [`Dockerfile`](file:///d:/Product-Catalog/frontend/Dockerfile) áp dụng kỹ thuật **Multi-stage Build**:
- **Stage 1 (Build):** Dùng `node:20-alpine`, cài đặt thư viện và chạy `npm run build` để biên dịch mã JSX thành file tĩnh trong thư mục `/dist`.
- **Stage 2 (Runtime):** Dùng `nginx:alpine` siêu nhỏ gọn, chỉ copy thư mục `/dist` từ Stage 1 sang `/usr/share/nginx/html`.
- **Cấu hình Nginx (`nginx.conf`):**
  - Kích hoạt nén **Gzip** cho JS, CSS, JSON và hình ảnh.
  - Cấu hình Cache 1 tháng cho tài nguyên tĩnh.
  - Reverse proxy các request API (`/Thuancyber/` và `/api/v1/`) sang dịch vụ backend cổng 8000.
  - Khắc phục lỗi 404 của Single Page Application bằng chỉ thị:
    `try_files $uri $uri/ /index.html;`

---

## 5. Hướng dẫn Khởi chạy Môi trường Phát triển (Local Dev)

```bash
cd frontend

# Cài đặt thư viện dependencies
npm install

# Khởi chạy Vite Dev Server
npm run dev
```

Giao diện sẽ chạy tại địa chỉ: [http://localhost:5173](http://localhost:5173). Mọi request API sẽ được Vite Proxy tự động chuyển tiếp sang Backend đang chạy tại `http://localhost:8000`.
