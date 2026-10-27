import Button from '../components/common/Button'

/**
 * Route guard kiểm tra vai trò người dùng (ví dụ: chỉ cho phép 'admin').
 */
export default function RoleGuard({
  currentUser,
  allowedRoles = ['admin'],
  children,
  onBack,
  onOpenLogin,
}) {
  const userRole = currentUser?.role_name || ''
  const hasPermission = allowedRoles.includes(userRole)

  if (!hasPermission) {
    return (
      <div className="card" style={{ maxWidth: 600, margin: '60px auto', textAlign: 'center', padding: 40 }}>
        <i className="fa-solid fa-shield-halved fa-4x" style={{ color: 'var(--danger)', marginBottom: 16 }}></i>
        <h2 style={{ color: 'var(--accent-red)', marginBottom: 12 }}>403 — Quyền Truy Cập Bị Từ Chối</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 24 }}>
          Khu vực này được bảo mật và chỉ dành cho tài khoản có vai trò{' '}
          <strong>{allowedRoles.join(', ')}</strong>.
          {currentUser ? (
            <span> Tài khoản hiện tại của bạn là <strong>{currentUser.email}</strong> (Vai trò: <strong>{userRole}</strong>).</span>
          ) : (
            <span> Bạn chưa đăng nhập vào hệ thống.</span>
          )}
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
          {onBack && (
            <Button variant="outline" onClick={onBack}>
              <i className="fa-solid fa-arrow-left"></i> Quay Lại
            </Button>
          )}
          {onOpenLogin && (
            <Button variant="primary" onClick={onOpenLogin}>
              <i className="fa-solid fa-key"></i> Đăng Nhập Tài Khoản Phù Hợp
            </Button>
          )}
        </div>
      </div>
    )
  }

  return children
}
