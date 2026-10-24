import { useState } from 'react'
import Button from '../../../components/common/Button'
import Input from '../../../components/common/Input'
import { isValidEmail } from '../../../utils/validators'

export default function LoginForm({ onSubmit, loading, onSwitchToRegister }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [emailError, setEmailError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!isValidEmail(email)) {
      setEmailError('Vui lòng nhập định dạng email hợp lệ')
      return
    }
    setEmailError('')
    onSubmit({ email: email.trim(), password })
  }

  return (
    <form onSubmit={handleSubmit}>
      <Input
        label="Địa chỉ Email"
        type="email"
        required
        placeholder="user@example.com"
        value={email}
        onChange={(e) => {
          setEmail(e.target.value)
          if (emailError) setEmailError('')
        }}
        error={emailError}
        style={{ marginBottom: 14 }}
      />

      <Input
        label="Mật khẩu"
        type="password"
        required
        placeholder="Nhập mật khẩu..."
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{ marginBottom: 20 }}
      />

      <Button
        type="submit"
        variant="primary"
        loading={loading}
        style={{ width: '100%', marginBottom: 12 }}
      >
        <i className="fa-solid fa-right-to-bracket"></i> Đăng Nhập
      </Button>

      {onSwitchToRegister && (
        <div style={{ textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Chưa có tài khoản?{' '}
          <span
            style={{ color: 'var(--primary)', cursor: 'pointer', fontWeight: 500 }}
            onClick={onSwitchToRegister}
          >
            Đăng ký ngay
          </span>
        </div>
      )}
    </form>
  )
}
