import { useState } from 'react'
import Modal from '../../../components/common/Modal'
import { authService } from '../services/authService'
import LoginForm from './LoginForm'
import RegisterForm from './RegisterForm'

export default function AuthModal({ isOpen, onClose, onAuthSuccess, showToast }) {
  const [tab, setTab] = useState('login') // 'login' | 'register'
  const [loading, setLoading] = useState(false)

  if (!isOpen) return null

  const handleLoginSubmit = async (credentials) => {
    setLoading(true)
    try {
      await authService.login(credentials)
      showToast('Đăng nhập thành công!', 'success')
      if (onAuthSuccess) onAuthSuccess()
      onClose()
    } catch (err) {
      showToast(err.message || 'Lỗi đăng nhập', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleRegisterSubmit = async (payload) => {
    setLoading(true)
    try {
      await authService.register(payload)
      showToast('Đăng ký thành công! Hãy đăng nhập.', 'success')
      setTab('login')
    } catch (err) {
      showToast(err.message || 'Lỗi đăng ký', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={tab === 'login' ? 'Đăng Nhập Tài Khoản' : 'Đăng Ký Thành Viên'}
      icon={tab === 'login' ? 'fa-solid fa-lock' : 'fa-solid fa-user-plus'}
      maxWidth={460}
    >
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        <button
          type="button"
          className={`btn btn-sm ${tab === 'login' ? 'btn-primary' : 'btn-outline'}`}
          style={{ flex: 1 }}
          onClick={() => setTab('login')}
        >
          <i className="fa-solid fa-right-to-bracket"></i> Đăng Nhập
        </button>
        <button
          type="button"
          className={`btn btn-sm ${tab === 'register' ? 'btn-primary' : 'btn-outline'}`}
          style={{ flex: 1 }}
          onClick={() => setTab('register')}
        >
          <i className="fa-solid fa-user-plus"></i> Đăng Ký
        </button>
      </div>

      {tab === 'login' ? (
        <LoginForm
          onSubmit={handleLoginSubmit}
          loading={loading}
          onSwitchToRegister={() => setTab('register')}
        />
      ) : (
        <RegisterForm
          onSubmit={handleRegisterSubmit}
          loading={loading}
          onSwitchToLogin={() => setTab('login')}
        />
      )}
    </Modal>
  )
}
