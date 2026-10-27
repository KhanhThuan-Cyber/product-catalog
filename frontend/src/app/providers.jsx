import { createContext, useContext, useState } from 'react'
import { ThemeProvider } from '../context/ThemeContext'

// --- Toast Context ---
const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toast, setToast] = useState(null)

  const showToast = (message, type = 'success') => {
    setToast({ message, type })
    setTimeout(() => {
      setToast(null)
    }, 4000)
  }

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {toast && (
        <div className={`toast toast-${toast.type}`}>
          {toast.type === 'success' ? (
            <i className="fa-solid fa-circle-check" style={{ marginRight: 8 }}></i>
          ) : (
            <i className="fa-solid fa-triangle-exclamation" style={{ marginRight: 8 }}></i>
          )}
          {toast.message}
        </div>
      )}
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    return { showToast: (msg) => console.log(msg) }
  }
  return context
}

// --- Cart Context ---
const CartContext = createContext(null)

export function CartProvider({ children }) {
  const [cart, setCart] = useState([])

  const addToCart = (product) => {
    setCart((prev) => {
      const existing = prev.find((item) => item.product.id === product.id)
      if (existing) {
        return prev.map((item) =>
          item.product.id === product.id ? { ...item, qty: item.qty + 1 } : item
        )
      }
      return [...prev, { product, qty: 1 }]
    })
  }

  const updateQty = (productId, delta) => {
    setCart((prev) =>
      prev
        .map((item) => {
          if (item.product.id === productId) {
            const nextQty = item.qty + delta
            return nextQty > 0 ? { ...item, qty: nextQty } : null
          }
          return item
        })
        .filter(Boolean)
    )
  }

  const clearCart = () => setCart([])

  const totalItems = cart.reduce((sum, item) => sum + item.qty, 0)
  const totalPrice = cart.reduce((sum, item) => sum + item.qty * item.product.price, 0)

  return (
    <CartContext.Provider
      value={{
        cart,
        addToCart,
        updateQty,
        clearCart,
        totalItems,
        totalPrice,
      }}
    >
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const context = useContext(CartContext)
  if (!context) {
    throw new Error('useCart must be used within CartProvider')
  }
  return context
}

// --- Unified App Providers ---
export default function AppProviders({ children }) {
  return (
    <ThemeProvider>
      <ToastProvider>
        <CartProvider>{children}</CartProvider>
      </ToastProvider>
    </ThemeProvider>
  )
}
