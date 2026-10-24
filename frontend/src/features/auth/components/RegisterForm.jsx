import { useState } from 'react'
import Button from '../../../components/common/Button'
import Input from '../../../components/common/Input'
import { isValidEmail, isValidPassword } from '../../../utils/validators'

export default function RegisterForm({ onSubmit, loading, onSwitchToLogin }) {
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({})

  const handleSubmit = (e) => {
    e.preventDefault()
    const nextErrors = {}

    if (!isValidEmail(email)) {
      nextErrors.email = 'Vui lòng nhập email hợp lệ'
    }
    if (!isValidPassword(password)) {
      nextErrors.password = 'Mật khẩu phải có tối thiểu 6 ký tự'
    }

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors)
      return
    }

    setErrors({})
    onSubmit({
      email: email.trim(),
      password,
      full_name: fullName.trim() || null,
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <Input
        label="Họ và tên"
        type="text"
        placeholder="Nguyễn Văn A"
        value={fullName}
        onChange={(e) => setFullName(e.target.value)}
        style={{ marginBottom: 14 }}
      />

      <Input
        label="Địa chỉ Email"
        type="email"
        required
        placeholder="user@example.com"
        value={email}
        onChange={(e) => {
          setEmail(e.target.value)
          if (errors.email) setErrors((prev) => ({ ...prev, email: '' }))
        }}
        error={errors.email}
        style={{ marginBottom: 14 }}
      />

      <Input
        label="Mật khẩu"
        type="password"
        required
        placeholder="Tối thiểu 6 ký tự..."
        value={password}
        onChange={(e) => {
          setPassword(e.target.value)
          if (errors.password) setErrors((prev) => ({ ...prev, password: '' }))
        }}
        error={errors.password}
        style={{ marginBottom: 20 }}
      />

      <Button
        type="submit"
        variant="primary"
        loading={loading}
        style={{ width: '100%', marginBottom: 12 }}
      >
        <i className="fa-solid fa-user-plus"></i> Đăng Ký Tài Khoản
      </Button>

      {onSwitchToLogin && (
        <div style={{ textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Đã có tài khoản?{' '}
          <span
            style={{ color: 'var(--primary)', cursor: 'pointer', fontWeight: 500 }}
            onClick={onSwitchToLogin}
          >
            Đăng nhập
          </span>
        </div>
      )}
    </form>
  )
}
