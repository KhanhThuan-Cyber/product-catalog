import { api } from '../../../api/client'
import { ENDPOINTS } from '../../../api/endpoints'

export const categoryService = {
  /**
   * Lấy danh sách toàn bộ danh mục
   */
  list: async () => {
    return await api.get(ENDPOINTS.CATEGORIES.BASE)
  },

  /**
   * Xem chi tiết danh mục theo ID
   */
  getById: async (id) => {
    return await api.get(ENDPOINTS.CATEGORIES.BY_ID(id))
  },

  /**
   * Tạo danh mục mới
   */
  create: async (data) => {
    return await api.post(ENDPOINTS.CATEGORIES.BASE, data)
  },

  /**
   * Cập nhật danh mục
   */
  update: async (id, data) => {
    return await api.put(ENDPOINTS.CATEGORIES.BY_ID(id), data)
  },

  /**
   * Xóa danh mục
   */
  delete: async (id) => {
    return await api.delete(ENDPOINTS.CATEGORIES.BY_ID(id))
  },
}
