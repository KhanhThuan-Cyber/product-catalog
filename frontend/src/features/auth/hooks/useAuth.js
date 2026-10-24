import { useCallback, useEffect, useState } from 'react'
import { authService } from '../services/authService'
import { getToken } from '../utils/token'

export function useAuth() {
  const [currentUser, setCurrentUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchUser = useCallback(async () => {
    const token = getToken()
    if (!token) {
      setCurrentUser(null)
      setLoading(false)
      return
    }

    try {
      const user = await authService.getMe()
      setCurrentUser(user)
    } catch {
      authService.logout()
      setCurrentUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  const login = async (credentials) => {
    const res = await authService.login(credentials)
    await fetchUser()
    return res
  }

  const register = async (payload) => {
    return await authService.register(payload)
  }

  const logout = () => {
    authService.logout()
    setCurrentUser(null)
  }

  const updateUser = (updated) => {
    setCurrentUser(updated)
  }

  const isAdmin = currentUser?.role_name === 'admin'

  return {
    currentUser,
    loading,
    isAdmin,
    login,
    register,
    logout,
    updateUser,
    refreshUser: fetchUser,
  }
}
