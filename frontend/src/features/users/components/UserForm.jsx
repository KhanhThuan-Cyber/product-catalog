import { useEffect, useState } from 'react'
import Button from '../../../components/common/Button'
import Input from '../../../components/common/Input'
import Modal from '../../../components/common/Modal'
import { isValidEmail, isValidPassword } from '../../../utils/validators'

export default function UserForm({
  isOpen,
  onClose,
  onSubmit,
  roles = [],
  loading = false,
}) {
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [roleId, setRoleId] = useState('')
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (isOpen) {
      setEmail('')
      setFullName('')
      setPassword('')
      if (roles.length > 0) {
        const defaultRole = roles.find((r) => r.name === 'user') || roles[0]
        setRoleId(defaultRole.id)
      }
      setErrors({})
    }
  }, [isOpen, roles])

  const handleSubmit = (e) => {
    e.preventDefault()
    const nextErrors = {}

    if (!isValidEmail(email)) nextErrors.email = 'Vui lòng nhập email hợp lệ'
    if (!isValidPassword(password)) nextErrors.password = 'Mật khẩu phải tối thiểu 6 ký tự'
    if (!roleId) nextErrors.role = 'Vui lòng chọn vai trò'

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors)
      return
    }

    setErrors({})
    onSubmit({
      email: email.trim(),
      full_name: fullName.trim() || null,
      password,
      role_id: parseInt(roleId, 10),
    })
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Thêm Người Dùng Mới"
      icon="fa-solid fa-user-plus"
      maxWidth={480}
    >
      <form onSubmit={handleSubmit}>
        <Input
          label="Địa chỉ Email"
          type="email"
          required
          placeholder="user@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={errors.email}
          style={{ marginBottom: 14 }}
        />

        <Input
          label="Họ và tên"
          type="text"
          placeholder="Nhập họ và tên..."
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          style={{ marginBottom: 14 }}
        />

        <Input
          label="Mật khẩu khởi tạo"
          type="password"
          required
          placeholder="Tối thiểu 6 ký tự..."
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={errors.password}
          style={{ marginBottom: 14 }}
        />

        <div className="form-group" style={{ marginBottom: 20 }}>
          <label>Vai trò hệ thống *</label>
          <select
            value={roleId}
            onChange={(e) => setRoleId(e.target.value)}
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
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Hủy
          </Button>
          <Button type="submit" variant="primary" loading={loading}>
            <i className="fa-solid fa-check"></i> Tạo Tài Khoản
          </Button>
        </div>
      </form>
    </Modal>
  )
}
