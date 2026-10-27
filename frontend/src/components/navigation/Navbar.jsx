import ThemeToggle from '../common/ThemeToggle'

export default function Navbar({
  currentView,
  onNavigate,
  currentUser,
  isAdmin,
  cartCount = 0,
  onOpenCart,
  onOpenAuth,
  onLogout,
}) {
  return (
    <header className="navbar">
      <div className="brand" onClick={() => onNavigate('store')}>
        <h1>
          {/* color được lấy từ brand h1 → var(--accent-sky) trong layout.css */}
          <i className="fa-solid fa-cube"></i>
          ProductCatalog
        </h1>
        <div className="subtitle">
          {currentView === 'store'
            ? 'Cửa Hàng Mua Sắm Trực Tuyến'
            : currentView === 'admin'
            ? 'Cổng Quản Trị Hệ Thống (Admin)'
            : 'Trang Cá Nhân & Hồ Sơ'}
        </div>
      </div>

      <div className="nav-actions">
        {/* Nút quay về cửa hàng */}
        {currentView !== 'store' && (
          <button className="btn btn-sm btn-outline" onClick={() => onNavigate('store')}>
            <i className="fa-solid fa-store"></i> Cửa Hàng
          </button>
        )}

        {/* Nút Admin — dùng CSS variable thay vì hardcode */}
        {isAdmin && (
          <button
            className={`btn btn-sm ${currentView === 'admin' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => onNavigate('admin')}
            style={{
              borderColor: 'var(--accent-violet)',
              color: currentView === 'admin' ? 'var(--text-on-accent)' : 'var(--accent-purple)',
              background: currentView === 'admin' ? 'var(--accent-violet)' : 'transparent',
            }}
          >
            <i className="fa-solid fa-gauge-high"></i> Trang Admin
          </button>
        )}

        {/* Nút giỏ hàng */}
        {currentView === 'store' && onOpenCart && (
          <button
            className="btn btn-sm btn-secondary"
            onClick={onOpenCart}
            style={{ position: 'relative' }}
          >
            <i className="fa-solid fa-cart-shopping"></i> Giỏ Hàng
            {cartCount > 0 && (
              <span
                style={{
                  background: 'var(--danger)',
                  color: 'var(--text-on-accent)',
                  borderRadius: '10px',
                  padding: '1px 6px',
                  fontSize: '0.7rem',
                  marginLeft: 6,
                  fontWeight: 700,
                }}
              >
                {cartCount}
              </span>
            )}
          </button>
        )}

        {/* Theme Toggle */}
        <ThemeToggle />

        {/* Thông tin User hoặc Nút Đăng nhập */}
        {currentUser ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <button
              className={`btn btn-sm ${currentView === 'profile' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => onNavigate('profile')}
              title="Mở Trang Cá Nhân"
            >
              <i className="fa-solid fa-circle-user" style={{ color: 'var(--accent-blue)' }}></i>
              <span>{currentUser.full_name || currentUser.email}</span>
              <span className={`role-tag role-${currentUser.role_name}`} style={{ marginLeft: 6 }}>
                {currentUser.role_name}
              </span>
            </button>

            <button className="btn btn-sm btn-outline" onClick={onLogout} title="Đăng xuất">
              <i className="fa-solid fa-right-from-bracket"></i>
            </button>
          </div>
        ) : (
          <button className="btn btn-sm btn-primary" onClick={onOpenAuth}>
            <i className="fa-solid fa-key"></i> Đăng Nhập / Đăng Ký
          </button>
        )}
      </div>
    </header>
  )
}
