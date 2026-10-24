import { getToken, removeToken, setToken } from '../features/auth/utils/token'
import { API_PREFIX } from './endpoints'
import { parseApiError } from './errorHandler'

export { getToken, removeToken, setToken }

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

async function request(method, path, body = null, params = null) {
  // Chuẩn hóa path nếu đã có prefix hoặc chưa
  const cleanPath = path.startsWith(API_PREFIX) ? path : `${API_PREFIX}${path.startsWith('/') ? path : `/${path}`}`
  let url = cleanPath

  if (params) {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        searchParams.append(key, value)
      }
    })
    const queryString = searchParams.toString()
    if (queryString) {
      url += `?${queryString}`
    }
  }

  const headers = {
    'Content-Type': 'application/json',
  }

  const token = getToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const startTime = Date.now()
  const logEntry = {
    id: Math.random().toString(36).substring(2, 9),
    timestamp: new Date().toLocaleTimeString(),
    method,
    url,
    requestBody: body,
    status: null,
    durationMs: 0,
    responseBody: null,
    error: false,
  }

  try {
    const options = { method, headers }
    if (body && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      options.body = JSON.stringify(body)
    }

    const res = await fetch(url, options)
    logEntry.status = res.status
    logEntry.durationMs = Date.now() - startTime

    if (res.status === 204) {
      logEntry.responseBody = null
      broadcastLog(logEntry)
      return null
    }

    const data = await res.json().catch(() => null)
    logEntry.responseBody = data

    if (!res.ok) {
      logEntry.error = true
      broadcastLog(logEntry)
      const errorMsg = parseApiError({ data, message: `HTTP Error ${res.status}` })
      const err = new Error(errorMsg)
      err.status = res.status
      err.data = data
      throw err
    }

    broadcastLog(logEntry)
    return data
  } catch (err) {
    if (!logEntry.status) {
      logEntry.status = 'FAILED'
      logEntry.durationMs = Date.now() - startTime
      logEntry.error = true
      logEntry.responseBody = { error: err.message }
      broadcastLog(logEntry)
    }
    throw err
  }
}

export const api = {
  get: (path, params) => request('GET', path, null, params),
  post: (path, body) => request('POST', path, body),
  put: (path, body) => request('PUT', path, body),
  patch: (path, body) => request('PATCH', path, body),
  delete: (path) => request('DELETE', path),
}
