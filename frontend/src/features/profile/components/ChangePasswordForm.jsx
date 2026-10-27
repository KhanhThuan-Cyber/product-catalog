import { useState } from 'react'
import Button from '../../../components/common/Button'
import Input from '../../../components/common/Input'
import { profileService } from '../services/profileService'

export default function ChangePasswordForm({ showToast }) {
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  const handleSubmit = async (e) => {
    e.preventDefault()
    const nextErrors = {}

    if (!oldPassword) nextErrors.old = 'Vui lòng nhập mật khẩu hiện tại'
    if (newPassword.length < 6) nextErrors.new = 'Mật khẩu mới tối thiểu 6 ký tự'
    if (newPassword !== confirmPassword) nextErrors.confirm = 'Mật khẩu xác nhận không khớp'

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors)
      return
    }

    setErrors({})
    setLoading(true)
    try {
      await profileService.changePassword({
        old_password: oldPassword,
        new_password: newPassword,
      })
      showToast('Đổi mật khẩu thành công!', 'success')
      setOldPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err) {
      showToast(err.message || 'Đổi mật khẩu thất bại', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card" style={{ height: '100%' }}>
      <div className="card-title" style={{ fontSize: '1.05rem', marginBottom: 16 }}>
        <span>
          <i className="fa-solid fa-key" style={{ color: 'var(--accent-amber)', marginRight: 8 }}></i>
          Đổi Mật Khẩu
        </span>
      </div>

      <form onSubmit={handleSubmit}>
        <Input
          label="Mật khẩu hiện tại"
          type="password"
          required
          placeholder="Nhập mật khẩu hiện tại..."
          value={oldPassword}
          onChange={(e) => setOldPassword(e.target.value)}
          error={errors.old}
          style={{ marginBottom: 14 }}
        />

        <Input
          label="Mật khẩu mới"
          type="password"
          required
          placeholder="Tối thiểu 6 ký tự..."
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          error={errors.new}
          style={{ marginBottom: 14 }}
        />

        <Input
          label="Xác nhận mật khẩu mới"
          type="password"
          required
          placeholder="Nhập lại mật khẩu mới..."
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          error={errors.confirm}
          style={{ marginBottom: 20 }}
        />

        <Button type="submit" variant="secondary" loading={loading} style={{ width: '100%' }}>
          <i className="fa-solid fa-shield-halved"></i> Cập Nhật Mật Khẩu
        </Button>
      </form>
    </div>
  )
}
