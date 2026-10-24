import { useEffect, useState } from 'react'
import Button from '../../../components/common/Button'
import Input from '../../../components/common/Input'
import { profileService } from '../services/profileService'

export default function ProfileForm({ currentUser, onProfileUpdated, showToast }) {
  const [fullName, setFullName] = useState(currentUser?.full_name || '')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setFullName(currentUser?.full_name || '')
  }, [currentUser])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!fullName.trim()) {
      showToast('Họ và tên không được để trống', 'error')
      return
    }

    setLoading(true)
    try {
      const updated = await profileService.updateProfile({ full_name: fullName.trim() })
      showToast('Cập nhật thông tin thành công!', 'success')
      if (onProfileUpdated) onProfileUpdated(updated)
    } catch (err) {
      showToast(err.message || 'Lỗi cập nhật thông tin', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card" style={{ height: '100%' }}>
      <div className="card-title" style={{ fontSize: '1.05rem', marginBottom: 16 }}>
        <span>
          <i className="fa-solid fa-user-pen" style={{ color: '#38bdf8', marginRight: 8 }}></i>
          Thông Tin Cá Nhân
        </span>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group" style={{ marginBottom: 14 }}>
          <label>Email Đăng Ký (Không thể sửa)</label>
          <input
            type="email"
            disabled
            value={currentUser?.email || ''}
            style={{ opacity: 0.6, cursor: 'not-allowed' }}
          />
        </div>

        <Input
          label="Họ và tên hiển thị"
          required
          placeholder="Nhập họ và tên..."
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          style={{ marginBottom: 20 }}
        />

        <Button type="submit" variant="primary" loading={loading} style={{ width: '100%' }}>
          <i className="fa-solid fa-floppy-disk"></i> Lưu Thay Đổi
        </Button>
      </form>
    </div>
  )
}
