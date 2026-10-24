import Button from '../components/common/Button'

/**
 * Route guard kiểm tra đăng nhập. Nếu chưa đăng nhập, hiển thị thông báo yêu cầu đăng nhập.
 */
export default function AuthGuard({
  currentUser,
  children,
  onOpenLogin,
  fallback = null,
}) {
  if (!currentUser) {
    if (fallback) return fallback

    return (
      <div className="card" style={{ maxWidth: 500, margin: '60px auto', textAlign: 'center', padding: 40 }}>
        <i className="fa-solid fa-lock fa-3x" style={{ color: '#f59e0b', marginBottom: 16 }}></i>
        <h3 style={{ marginBottom: 8 }}>Yêu Cầu Đăng Nhập</h3>
        <p style={{ color: 'var(--text-muted)', marginBottom: 20 }}>
          Vui lòng đăng nhập tài khoản để truy cập nội dung này.
        </p>
        <Button variant="primary" onClick={onOpenLogin}>
          <i className="fa-solid fa-key"></i> Đăng Nhập Ngay
        </Button>
      </div>
    )
  }

  return children
}
