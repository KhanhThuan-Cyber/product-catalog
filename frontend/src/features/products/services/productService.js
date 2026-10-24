import { api } from '../../../api/client'
import { ENDPOINTS } from '../../../api/endpoints'

export const productService = {
  /**
   * Lấy danh sách sản phẩm phân trang và lọc
   */
  listPaginated: async (params) => {
    return await api.get(ENDPOINTS.PRODUCTS.BASE, params)
  },

  /**
   * Xem chi tiết sản phẩm theo ID
   */
  getById: async (id) => {
    return await api.get(ENDPOINTS.PRODUCTS.BY_ID(id))
  },

  /**
   * Tạo sản phẩm mới
   */
  create: async (data) => {
    return await api.post(ENDPOINTS.PRODUCTS.BASE, data)
  },

  /**
   * Cập nhật toàn bộ thông tin sản phẩm (PUT)
   */
  update: async (id, data) => {
    return await api.put(ENDPOINTS.PRODUCTS.BY_ID(id), data)
  },

  /**
   * Cập nhật một phần sản phẩm (PATCH)
   */
  patch: async (id, data) => {
    return await api.patch(ENDPOINTS.PRODUCTS.BY_ID(id), data)
  },

  /**
   * Xóa sản phẩm
   */
  delete: async (id) => {
    return await api.delete(ENDPOINTS.PRODUCTS.BY_ID(id))
  },
}
