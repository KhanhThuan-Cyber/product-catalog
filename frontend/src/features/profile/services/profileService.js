import { api } from '../../../api/client'
import { ENDPOINTS } from '../../../api/endpoints'

export const profileService = {
  /**
   * Cập nhật thông tin cá nhân (họ và tên)
   */
  updateProfile: async (payload) => {
    return await api.patch(ENDPOINTS.AUTH.ME, payload)
  },

  /**
   * Đổi mật khẩu cá nhân
   */
  changePassword: async (payload) => {
    return await api.post(ENDPOINTS.AUTH.CHANGE_PASSWORD, payload)
  },
}
