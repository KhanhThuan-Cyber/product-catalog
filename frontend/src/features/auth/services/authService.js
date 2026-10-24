import { api } from '../../../api/client'
import { ENDPOINTS } from '../../../api/endpoints'
import { removeToken, setToken } from '../utils/token'

export const authService = {
  /**
   * Đăng ký tài khoản mới
   */
  register: async (payload) => {
    return await api.post(ENDPOINTS.AUTH.REGISTER, payload)
  },

  /**
   * Đăng nhập lấy access_token
   */
  login: async (credentials) => {
    const res = await api.post(ENDPOINTS.AUTH.LOGIN, credentials)
    if (res?.access_token) {
      setToken(res.access_token)
    }
    return res
  },

  /**
   * Lấy thông tin user hiện tại
   */
  getMe: async () => {
    return await api.get(ENDPOINTS.AUTH.ME)
  },

  /**
   * Cập nhật thông tin cá nhân (họ tên)
   */
  updateProfile: async (payload) => {
    return await api.patch(ENDPOINTS.AUTH.ME, payload)
  },

  /**
   * Đổi mật khẩu
   */
  changePassword: async (payload) => {
    return await api.post(ENDPOINTS.AUTH.CHANGE_PASSWORD, payload)
  },

  /**
   * Đăng xuất
   */
  logout: () => {
    removeToken()
  },
}
