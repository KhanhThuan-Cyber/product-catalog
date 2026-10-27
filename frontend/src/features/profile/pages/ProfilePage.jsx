import Button from '../../../components/common/Button'
import ChangePasswordForm from '../components/ChangePasswordForm'
import ProfileForm from '../components/ProfileForm'

export default function ProfilePage({
  currentUser,
  onProfileUpdated,
  onBackToStore,
  onGoToAdmin,
  onLogout,
  showToast,
}) {
  const isAdmin = currentUser?.role_name === 'admin'

  return (
    <div style={{ maxWidth: 900, margin: '0 auto' }}>
      {/* Profile Header */}
      <div className="card" style={{ padding: '28px 32px', marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
            <div style={{ color: isAdmin ? 'var(--accent-purple)' : 'var(--accent-blue)' }}>
              <i className="fa-solid fa-circle-user" style={{ fontSize: '4.5rem' }}></i>
            </div>
            <div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-heading)', marginBottom: 4 }}>
                {currentUser?.full_name || 'Người dùng chưa đặt tên'}
              </h2>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 8 }}>
                <i className="fa-regular fa-envelope" style={{ marginRight: 6 }}></i>
                {currentUser?.email}
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                <span className={`role-tag role-${currentUser?.role_name || 'user'}`}>
                  <i className={isAdmin ? 'fa-solid fa-shield-halved' : 'fa-solid fa-user'} style={{ marginRight: 4 }}></i>
                  {currentUser?.role_name}
                </span>
                <span className="badge badge-active">
                  <i className="fa-solid fa-circle-check" style={{ marginRight: 4 }}></i>
                  Đang hoạt động
                </span>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            {onBackToStore && (
              <Button variant="outline" size="sm" icon="fa-solid fa-store" onClick={onBackToStore}>
                Về Cửa Hàng
              </Button>
            )}
            {isAdmin && onGoToAdmin && (
              <Button variant="primary" size="sm" icon="fa-solid fa-gauge-high" onClick={onGoToAdmin}>
                Trang Admin
              </Button>
            )}
            {onLogout && (
              <Button variant="danger" size="sm" icon="fa-solid fa-right-from-bracket" onClick={onLogout}>
                Đăng Xuất
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Two columns: Profile Form & Change Password */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
        <ProfileForm
          currentUser={currentUser}
          onProfileUpdated={onProfileUpdated}
          showToast={showToast}
        />
        <ChangePasswordForm showToast={showToast} />
      </div>
    </div>
  )
}
