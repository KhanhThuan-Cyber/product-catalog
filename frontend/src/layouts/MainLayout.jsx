import Navbar from '../components/navigation/Navbar'

export default function MainLayout({
  children,
  currentView,
  onNavigate,
  currentUser,
  isAdmin,
  cartCount,
  onOpenCart,
  onOpenAuth,
  onLogout,
}) {
  return (
    <div className="app-container">
      <Navbar
        currentView={currentView}
        onNavigate={onNavigate}
        currentUser={currentUser}
        isAdmin={isAdmin}
        cartCount={cartCount}
        onOpenCart={onOpenCart}
        onOpenAuth={onOpenAuth}
        onLogout={onLogout}
      />
      <main>{children}</main>
    </div>
  )
}
