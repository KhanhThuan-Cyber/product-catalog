import { createContext, useContext, useEffect, useState } from 'react'

const RouterContext = createContext(null)

export function RouterProvider({ children, initialPath = 'store' }) {
  const [currentPath, setCurrentPath] = useState(() => {
    // Ưu tiên đọc từ hash trong URL nếu có (ví dụ #admin, #profile, #store)
    const hash = window.location.hash.replace('#', '')
    return hash || initialPath
  })

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '')
      if (hash) {
        setCurrentPath(hash)
      }
    }

    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  const navigate = (path) => {
    window.location.hash = path
    setCurrentPath(path)
  }

  return (
    <RouterContext.Provider value={{ currentPath, navigate }}>
      {children}
    </RouterContext.Provider>
  )
}

export function useRouter() {
  const context = useContext(RouterContext)
  if (!context) {
    throw new Error('useRouter must be used within RouterProvider')
  }
  return context
}
