/**
 * Kiểm tra địa chỉ email hợp lệ.
 * @param {string} email
 * @returns {boolean}
 */
export function isValidEmail(email) {
  if (!email || typeof email !== 'string') return false
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email.trim())
}

/**
 * Kiểm tra mật khẩu (tối thiểu 6 ký tự).
 * @param {string} password
 * @returns {boolean}
 */
export function isValidPassword(password) {
  return typeof password === 'string' && password.length >= 6
}

/**
 * Kiểm tra tên mã Role (chữ cái, số, gạch dưới, gạch nối, 2-50 ký tự).
 * @param {string} name
 * @returns {boolean}
 */
export function isValidRoleName(name) {
  if (!name || typeof name !== 'string') return false
  const re = /^[a-zA-Z0-9_\-]+$/
  const trimmed = name.trim()
  return trimmed.length >= 2 && trimmed.length <= 50 && re.test(trimmed)
}

/**
 * Kiểm tra giá bán sản phẩm (> 0).
 * @param {number|string} price
 * @returns {boolean}
 */
export function isValidPrice(price) {
  const num = parseFloat(price)
  return !isNaN(num) && num > 0
}

/**
 * Kiểm tra số lượng tồn kho (>= 0).
 * @param {number|string} stock
 * @returns {boolean}
 */
export function isValidStock(stock) {
  const num = parseInt(stock, 10)
  return !isNaN(num) && num >= 0
}

/**
 * Kiểm tra URL hình ảnh hợp lệ (http/https, tối đa 500 ký tự).
 * Trả về true nếu chuỗi rỗng (field không bắt buộc).
 * @param {string} url
 * @returns {boolean}
 */
export function isValidImageUrl(url) {
  if (!url || !url.trim()) return true // optional field
  if (url.trim().length > 500) return false
  try {
    const parsed = new URL(url.trim())
    return parsed.protocol === 'http:' || parsed.protocol === 'https:'
  } catch {
    return false
  }
}
