import { api } from '../../../api/client'
import { ENDPOINTS } from '../../../api/endpoints'

export const userService = {
  /**
   * Lấy danh sách tất cả người dùng (yêu cầu Admin)
   */
  list: async () => {
    return await api.get(ENDPOINTS.USERS.BASE)
  },

  /**
   * Tạo tài khoản người dùng mới bởi Admin
   */
  create: async (data) => {
    return await api.post(ENDPOINTS.USERS.BASE, data)
  },

  /**
   * Khóa hoặc mở khóa tài khoản
   */
  toggleStatus: async (userId, isActive) => {
    return await api.patch(ENDPOINTS.USERS.STATUS(userId), { is_active: isActive })
  },

  /**
   * Thay đổi vai trò (Role) của người dùng
   */
  changeRole: async (userId, roleId) => {
    return await api.patch(ENDPOINTS.USERS.ROLE(userId), { role_id: roleId })
  },

  /**
   * Lấy danh sách tất cả các Role khả dụng
   */
  listRoles: async () => {
    return await api.get(ENDPOINTS.USERS.ROLES).catch(() => api.get(ENDPOINTS.USERS.ROLES_ALL))
  },

  /**
   * Tạo Role mới trong hệ thống
   */
  createRole: async (roleData) => {
    return await api.post(ENDPOINTS.USERS.ROLES, roleData)
  },
}
