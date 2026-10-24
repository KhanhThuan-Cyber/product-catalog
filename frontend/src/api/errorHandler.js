/**
 * Chuẩn hóa và trích xuất thông báo lỗi từ phản hồi HTTP hoặc Exception.
 * @param {Error|object|string} error
 * @returns {string}
 */
export function parseApiError(error) {
  if (!error) return 'Đã có lỗi xảy ra. Vui lòng thử lại sau.'

  // Nếu là chuỗi trực tiếp
  if (typeof error === 'string') return error

  // Nếu có data trả về từ Backend FastAPI (thường nằm ở `detail`)
  const detail = error.data?.detail || error.response?.data?.detail || error.detail

  if (typeof detail === 'string') {
    return detail
  }

  // Nếu detail là mảng lỗi validation của Pydantic (422)
  if (Array.isArray(detail)) {
    const messages = detail.map((err) => {
      const field = err.loc ? err.loc.slice(1).join('.') : ''
      return field ? `${field}: ${err.msg}` : err.msg
    })
    return messages.join(', ')
  }

  // Nếu error có message
  if (error.message) {
    return error.message
  }

  return 'Không thể kết nối đến máy chủ Backend'
}
