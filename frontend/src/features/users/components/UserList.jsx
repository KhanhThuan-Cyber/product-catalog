import { useState } from 'react'
import Button from '../../../components/common/Button'
import Modal from '../../../components/common/Modal'

export default function UserList({
  users = [],
  roles = [],
  currentUser,
  onToggleStatus,
  onChangeRole,
}) {
  const [changingUser, setChangingUser] = useState(null)
  const [targetRoleId, setTargetRoleId] = useState('')
  const [loading, setLoading] = useState(false)

  const openChangeRoleModal = (u) => {
    setChangingUser(u)
    setTargetRoleId(u.role_id)
  }

  const handleRoleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await onChangeRole(changingUser.id, parseInt(targetRoleId, 10))
      setChangingUser(null)
    } finally {
      setLoading(false)
    }
  }

  const getRoleIcon = (roleName) => {
    switch (roleName) {
      case 'admin':
        return 'fa-solid fa-shield-halved'
      case 'user':
        return 'fa-solid fa-user'
      case 'manager':
        return 'fa-solid fa-briefcase'
      case 'editor':
        return 'fa-solid fa-pen-nib'
      default:
        return 'fa-solid fa-user-shield'
    }
  }

  if (users.length === 0) {
    return (
      <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '30px 0' }}>
        Chưa có người dùng nào.
      </p>
    )
  }

  return (
    <>
      <div className="table-responsive">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Người Dùng (Họ Tên & Email)</th>
              <th>Vai Trò (Role)</th>
              <th>Trạng Thái</th>
              <th>Ngày Đăng Ký</th>
              <th>Thao Tác Quản Trị</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => {
              const isCurrent = u.id === currentUser?.id
              return (
                <tr key={u.id}>
                  <td><strong>#{u.id}</strong></td>
                  <td>
                    <div>
                      <strong>{u.full_name || '—'}</strong>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                        <i className="fa-regular fa-envelope" style={{ marginRight: 4 }}></i>
                        {u.email} {isCurrent && <span style={{ color: 'var(--accent-emerald)' }}>(Bạn)</span>}
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className={`role-tag role-${u.role_name || 'default'}`}>
                      <i className={getRoleIcon(u.role_name)} style={{ marginRight: 4 }}></i>
                      {u.role_name}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${u.is_active ? 'badge-active' : 'badge-inactive'}`}>
                      <i className={u.is_active ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-xmark'} style={{ marginRight: 4 }}></i>
                      {u.is_active ? 'Hoạt động' : 'Bị khóa'}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    {u.created_at ? new Date(u.created_at).toLocaleDateString('vi-VN') : '—'}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <Button
                        size="sm"
                        variant="secondary"
                        icon="fa-solid fa-id-badge"
                        disabled={isCurrent}
                        onClick={() => openChangeRoleModal(u)}
                        title={isCurrent ? 'Không thể tự đổi vai trò của mình' : 'Đổi vai trò'}
                      >
                        Đổi Role
                      </Button>

                      <Button
                        size="sm"
                        variant={u.is_active ? 'danger' : 'success'}
                        icon={u.is_active ? 'fa-solid fa-lock' : 'fa-solid fa-lock-open'}
                        disabled={isCurrent}
                        onClick={() => onToggleStatus(u)}
                        title={isCurrent ? 'Không thể tự khóa tài khoản của mình' : (u.is_active ? 'Khóa tài khoản' : 'Mở khóa')}
                      >
                        {u.is_active ? 'Khóa' : 'Mở'}
                      </Button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Modal Đổi Vai Trò */}
      {changingUser && (
        <Modal
          isOpen={Boolean(changingUser)}
          onClose={() => setChangingUser(null)}
          title="Thay Đổi Vai Trò Người Dùng"
          icon="fa-solid fa-user-shield"
          maxWidth={420}
        >
          <form onSubmit={handleRoleSubmit}>
            <p style={{ fontSize: '0.9rem', marginBottom: 12 }}>
              Tài khoản: <strong>{changingUser.email}</strong>
            </p>

            <div className="form-group" style={{ marginBottom: 20 }}>
              <label>Chọn vai trò mới:</label>
              <select
                value={targetRoleId}
                onChange={(e) => setTargetRoleId(e.target.value)}
                required
              >
                {roles.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name.toUpperCase()} — {r.description || 'Không có mô tả'}
                  </option>
                ))}
              </select>
            </div>

            <div className="modal-footer">
              <Button variant="outline" onClick={() => setChangingUser(null)}>
                Hủy
              </Button>
              <Button type="submit" variant="primary" loading={loading}>
                <i className="fa-solid fa-check"></i> Lưu Vai Trò
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </>
  )
}
