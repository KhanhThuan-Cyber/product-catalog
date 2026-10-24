const TOKEN_KEY = 'access_token'

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY) || ''
  } catch {
    return ''
  }
}

export function setToken(token) {
  try {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token)
    } else {
      localStorage.removeItem(TOKEN_KEY)
    }
  } catch (err) {
    console.error('Không thể lưu token vào localStorage:', err)
  }
}

export function removeToken() {
  try {
    localStorage.removeItem(TOKEN_KEY)
  } catch (err) {
    console.error('Không thể xóa token khỏi localStorage:', err)
  }
}
