import axios from 'axios'
import { getToken, removeToken, setToken } from '../features/auth/utils/token'
import { API_PREFIX } from './endpoints'
import { parseApiError } from './errorHandler'

// Re-export token helpers (backward compat)
export { getToken, removeToken, setToken }

// ---------------------------------------------------------------------------
// ApiLogger pub/sub — giữ nguyên interface để ApiLogger component không đổi
// ---------------------------------------------------------------------------
let logListeners = []

export function subscribeApiLogs(listener) {
  logListeners.push(listener)
  return () => {
    logListeners = logListeners.filter((l) => l !== listener)
  }
}

function broadcastLog(log) {
  logListeners.forEach((listener) => listener(log))
}

// ---------------------------------------------------------------------------
// Axios instance
// ---------------------------------------------------------------------------
const axiosInstance = axios.create({
  // Không set baseURL vì path đã bao gồm API_PREFIX (/Thuancyber/...)
  headers: {
    'Content-Type': 'application/json',
  },
  // Lọc params: bỏ qua null, undefined, và chuỗi rỗng ''
  // (giữ đúng behavior của fetch cũ — Axios mặc định chỉ bỏ undefined)
  paramsSerializer: {
    serialize: (params) => {
      const clean = Object.fromEntries(
        Object.entries(params).filter(
          ([, v]) => v !== null && v !== undefined && v !== ''
        )
      )
      return new URLSearchParams(clean).toString()
    },
  },
})

// ---------------------------------------------------------------------------
// Request interceptor — inject auth token + khởi tạo log entry
// ---------------------------------------------------------------------------
axiosInstance.interceptors.request.use((config) => {
  // Inject Bearer token nếu có
  const token = getToken()
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }

  // Chuẩn hóa path: thêm API_PREFIX nếu chưa có
  if (config.url && !config.url.startsWith(API_PREFIX)) {
    config.url = `${API_PREFIX}${config.url.startsWith('/') ? config.url : `/${config.url}`}`
  }

  // Gắn metadata để response interceptor hoàn thiện log
  config.metadata = {
    startTime: Date.now(),
    logEntry: {
      id: Math.random().toString(36).substring(2, 9),
      timestamp: new Date().toLocaleTimeString(),
      method: config.method?.toUpperCase() ?? 'GET',
      url: config.url ?? '',
      requestBody: config.data ?? null,
      status: null,
      durationMs: 0,
      responseBody: null,
      error: false,
    },
  }

  return config
})

// ---------------------------------------------------------------------------
// Response interceptor — log, normalize 204, normalize error shape
// ---------------------------------------------------------------------------
axiosInstance.interceptors.response.use(
  // ✅ Success (2xx)
  (response) => {
    const { logEntry, startTime } = response.config.metadata ?? {}

    if (logEntry) {
      logEntry.status = response.status
      logEntry.durationMs = Date.now() - startTime
      // 204 No Content — axios trả '' hoặc undefined, normalize về null
      logEntry.responseBody = response.status === 204 ? null : response.data
      broadcastLog(logEntry)
    }

    // Giữ nguyên behavior fetch cũ: 204 → null, còn lại → data
    return response.status === 204 ? null : response.data
  },

  // ❌ Error (4xx, 5xx, network failure)
  (axiosError) => {
    const { logEntry, startTime } = axiosError.config?.metadata ?? {}

    if (logEntry) {
      logEntry.status = axiosError.response?.status ?? 'FAILED'
      logEntry.durationMs = Date.now() - startTime
      logEntry.error = true
      logEntry.responseBody = axiosError.response?.data ?? { error: axiosError.message }
      broadcastLog(logEntry)
    }

    // Normalize error về cùng shape với fetch cũ:
    //   err.message  — chuỗi đã được parseApiError
    //   err.status   — HTTP status code
    //   err.data     — raw response body từ backend
    const errorMsg = parseApiError(axiosError)
    const err = new Error(errorMsg)
    err.status = axiosError.response?.status ?? null
    err.data = axiosError.response?.data ?? null
    return Promise.reject(err)
  }
)

// ---------------------------------------------------------------------------
// Public API — giữ nguyên interface, không cần sửa bất kỳ caller nào
// ---------------------------------------------------------------------------
export const api = {
  get: (path, params) => axiosInstance.get(path, { params }),
  post: (path, body) => axiosInstance.post(path, body),
  put: (path, body) => axiosInstance.put(path, body),
  patch: (path, body) => axiosInstance.patch(path, body),
  delete: (path) => axiosInstance.delete(path),
}
