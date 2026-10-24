import Sidebar from '../components/navigation/Sidebar'
import RoleGuard from '../guards/RoleGuard'

export default function AdminLayout({
  children,
  currentTab,
  onSelectTab,
  currentUser,
  onBackToStore,
  onOpenLogin,
}) {
  return (
    <RoleGuard
      currentUser={currentUser}
      allowedRoles={['admin']}
      onBack={onBackToStore}
      onOpenLogin={onOpenLogin}
    >
      <div className="admin-portal">
        {/* Admin Header */}
        <div className="admin-header-bar">
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#fff' }}>
              <i className="fa-solid fa-gauge-high" style={{ color: '#c084fc', marginRight: 10 }}></i>
              Trung Tâm Quản Trị Hệ Thống (Admin Backoffice)
            </h2>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Toàn quyền quản trị cơ sở dữ liệu: Sản phẩm, Danh mục, Người dùng và Phân quyền Role
            </div>
          </div>
          <button className="btn btn-sm btn-outline" onClick={onBackToStore}>
            <i className="fa-solid fa-store"></i> Xem Cửa Hàng
          </button>
        </div>

        {/* Sidebar Navigation */}
        <Sidebar currentTab={currentTab} onSelectTab={onSelectTab} />

        {/* Content */}
        <div className="admin-content">{children}</div>
      </div>
    </RoleGuard>
  )
}
