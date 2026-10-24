import { useState } from 'react'
import Button from '../../../components/common/Button'
import Input from '../../../components/common/Input'
import Modal from '../../../components/common/Modal'
import { isValidRoleName } from '../../../utils/validators'

export default function RoleSelector({
  roles = [],
  selectedRoleId,
  onChange,
  onRoleCreated,
  showCreateButton = true,
  showToast,
  users = [],
}) {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [roleName, setRoleName] = useState('')
  const [roleDesc, setRoleDesc] = useState('')
  const [loading, setLoading] = useState(false)

  const handleCreateRole = async (e) => {
    e.preventDefault()
    const cleanName = roleName.trim().toLowerCase()
    if (!isValidRoleName(cleanName)) {
      if (showToast) {
        showToast('Tên vai trò chỉ gồm 2-50 ký tự (chữ cái, số, gạch dưới/nối)', 'error')
      }
      return
    }

    setLoading(true)
    try {
      if (onRoleCreated) {
        await onRoleCreated({ name: cleanName, description: roleDesc.trim() || null })
      }
      if (showToast) {
        showToast(`Đã thêm vai trò "${cleanName}" thành công!`, 'success')
      }
      setIsModalOpen(false)
      setRoleName('')
      setRoleDesc('')
    } catch (err) {
      if (showToast) {
        showToast(err.message || 'Lỗi khi tạo vai trò mới', 'error')
      }
    } finally {
      setLoading(false)
    }
  }

  const getRoleIcon = (name) => {
    switch (name) {
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

  return (
    <div>
      {/* Overview bar nếu có truyền users */}
      {users.length > 0 && (
        <div className="roles-summary-bar">
          <div className="roles-summary-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.9rem' }}>
              <i className="fa-solid fa-shield-halved" style={{ color: '#8b5cf6' }}></i>
              <strong>Vai Trò Hệ Thống ({roles.length}):</strong>
            </div>
            {showCreateButton && (
              <Button size="sm" variant="outline" icon="fa-solid fa-plus" onClick={() => setIsModalOpen(true)}>
                Tạo role mới
              </Button>
            )}
          </div>

          <div className="roles-chips-grid">
            {roles.map((r) => {
              const count = users.filter((u) => u.role_id === r.id).length
              return (
                <div key={r.id} className="role-chip-card">
                  <div className="role-chip-title">
                    <span className={`role-tag role-${r.name}`}>
                      <i className={getRoleIcon(r.name)} style={{ marginRight: 5 }}></i>
                      {r.name}
                    </span>
                    <span className="role-count-badge">
                      {count} user{count !== 1 ? 's' : ''}
                    </span>
                  </div>
                  <p className="role-chip-desc">{r.description || 'Không có mô tả'}</p>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Select input */}
      {onChange && (
        <div className="form-group">
          <label>Chọn vai trò</label>
          <div style={{ display: 'flex', gap: 8 }}>
            <select
              value={selectedRoleId}
              onChange={(e) => onChange(e.target.value)}
              style={{ flex: 1 }}
            >
              {roles.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name.toUpperCase()} — {r.description || 'Không có mô tả'}
                </option>
              ))}
            </select>
            {showCreateButton && !users.length && (
              <Button size="sm" variant="outline" icon="fa-solid fa-plus" onClick={() => setIsModalOpen(true)} title="Thêm vai trò mới">
                Thêm Role
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Modal Thêm Role Mới */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Thêm Vai Trò (Role) Mới"
        icon="fa-solid fa-shield-plus"
        maxWidth={460}
      >
        <form onSubmit={handleCreateRole}>
          <Input
            label="Tên Mã Vai Trò"
            required
            placeholder="Ví dụ: manager, staff, editor..."
            value={roleName}
            onChange={(e) => setRoleName(e.target.value)}
            helperText="2-50 ký tự (chữ cái, chữ số, gạch nối hoặc gạch dưới)."
            style={{ marginBottom: 14 }}
          />

          <div className="form-group" style={{ marginBottom: 20 }}>
            <label>Mô Tả Chức Năng</label>
            <textarea
              rows={3}
              placeholder="Mô tả quyền hạn hoặc trách nhiệm của vai trò này..."
              value={roleDesc}
              onChange={(e) => setRoleDesc(e.target.value)}
            />
          </div>

          <div className="modal-footer">
            <Button variant="outline" onClick={() => setIsModalOpen(false)} disabled={loading}>
              Hủy
            </Button>
            <Button type="submit" variant="primary" loading={loading}>
              <i className="fa-solid fa-check"></i> Tạo Vai Trò
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
