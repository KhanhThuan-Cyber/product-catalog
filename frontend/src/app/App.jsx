import { useEffect, useState } from 'react'
import AuthModal from '../features/auth/components/AuthModal'
import { useAuth } from '../features/auth/hooks/useAuth'
import CategoriesPage from '../features/categories/pages/CategoriesPage'
import { categoryService } from '../features/categories/services/categoryService'
import ProductCard from '../features/products/components/ProductCard'
import ProductPagination from '../features/products/components/ProductPagination'
import { useProducts } from '../features/products/hooks/useProducts'
import ProductsPage from '../features/products/pages/ProductsPage'
import ProfilePage from '../features/profile/pages/ProfilePage'
import UsersPage from '../features/users/pages/UsersPage'
import AuthGuard from '../guards/AuthGuard'
import AdminLayout from '../layouts/AdminLayout'
import MainLayout from '../layouts/MainLayout'
import { formatCurrency } from '../utils/formatCurrency'
import { useCart, useToast } from './providers'
import { useRouter } from './router'

// Live API Logger component
import ApiLogger from '../components/ApiLogger'

export default function App() {
  const { currentPath, navigate } = useRouter()
  const { currentUser, isAdmin, logout, updateUser, refreshUser } = useAuth()
  const { showToast } = useToast()
  const { cart, addToCart, updateQty, clearCart, totalItems, totalPrice } = useCart()

  const [categories, setCategories] = useState([])
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)
  const [isCartModalOpen, setIsCartModalOpen] = useState(false)
  const [adminTab, setAdminTab] = useState('products') // 'products' | 'categories' | 'users' | 'logs'

  // Modal xem chi tiết sản phẩm ở Storefront
  const [detailProduct, setDetailProduct] = useState(null)

  // Storefront products hook
  const {
    products: storeProducts,
    total: storeTotal,
    totalPages: storeTotalPages,
    loading: storeLoading,
    page: storePage,
    search: storeSearch,
    categoryId: storeCatId,
    setPage: setStorePage,
    setSearch: setStoreSearch,
    setCategoryId: setStoreCatId,
    refetch: refetchStoreProducts,
  } = useProducts({ pageSize: 8, sortBy: 'created_at', order: 'desc' })

  // Tải danh mục ban đầu
  useEffect(() => {
    categoryService.list().then((data) => setCategories(data || [])).catch(() => {})
  }, [])

  // Bảo vệ route Admin: nếu không phải Admin mà ở trang admin thì chuyển về store
  useEffect(() => {
    if (currentPath === 'admin' && !isAdmin) {
      navigate('store')
    }
  }, [currentPath, isAdmin, navigate])

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    setStorePage(1)
    refetchStoreProducts()
  }

  const handleAddToCartWithToast = (product) => {
    addToCart(product)
    showToast(`Đã thêm "${product.name}" vào giỏ hàng!`, 'success')
  }

  return (
    <MainLayout
      currentView={currentPath}
      onNavigate={navigate}
      currentUser={currentUser}
      isAdmin={isAdmin}
      cartCount={totalItems}
      onOpenCart={() => setIsCartModalOpen(true)}
      onOpenAuth={() => setIsAuthModalOpen(true)}
      onLogout={() => {
        logout()
        navigate('store')
        showToast('Đã đăng xuất tài khoản', 'success')
      }}
    >
      {/* 1. MÀN HÌNH CỬA HÀNG (STOREFRONT VIEW) */}
      {currentPath === 'store' && (
        <div className="storefront">
          {/* Hero Banner */}
          <div className="hero-banner" style={{ background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '36px 28px', marginBottom: 24, textAlign: 'center' }}>
            <h2 style={{ fontSize: '1.8rem', fontWeight: 700, color: '#fff', marginBottom: 8 }}>
              <i className="fa-solid fa-store" style={{ marginRight: 10, color: '#60a5fa' }}></i>
              Chào mừng đến với Cửa Hàng Trực Tuyến
            </h2>
            <p style={{ color: 'var(--text-muted)', maxWidth: 600, margin: '0 auto 20px auto', fontSize: '0.95rem' }}>
              Khám phá hàng loạt sản phẩm công nghệ, linh kiện và phụ kiện chính hãng giá ưu đãi nhất.
            </p>

            <form
              onSubmit={handleSearchSubmit}
              style={{
                display: 'flex',
                maxWidth: 650,
                margin: '0 auto',
                backgroundColor: 'var(--bg-input)',
                border: '1px solid var(--border)',
                borderRadius: '30px',
                padding: '4px 6px',
                alignItems: 'center',
              }}
            >
              <i className="fa-solid fa-magnifying-glass" style={{ paddingLeft: 16, color: 'var(--text-muted)' }}></i>
              <input
                type="text"
                placeholder="Tìm kiếm sản phẩm theo tên..."
                value={storeSearch}
                onChange={(e) => setStoreSearch(e.target.value)}
                style={{ flex: 1, background: 'transparent', border: 'none', padding: '10px 14px', color: '#fff' }}
              />
              <button type="submit" className="btn btn-primary" style={{ borderRadius: '24px', padding: '8px 20px' }}>
                Tìm Kiếm
              </button>
            </form>
          </div>

          {/* Category Chips Bar */}
          <div style={{ display: 'flex', gap: 10, overflowX: 'auto', paddingBottom: 12, marginBottom: 20 }}>
            <button
              className={`chip-btn ${storeCatId === '' ? 'active' : ''}`}
              onClick={() => { setStoreCatId(''); setStorePage(1); }}
              style={{
                backgroundColor: storeCatId === '' ? 'var(--primary)' : 'var(--bg-card)',
                border: '1px solid var(--border)',
                color: storeCatId === '' ? '#fff' : 'var(--text-muted)',
                padding: '8px 16px',
                borderRadius: '20px',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
              }}
            >
              <i className="fa-solid fa-border-all"></i> Tất Cả
            </button>
            {categories.map((cat) => (
              <button
                key={cat.id}
                className={`chip-btn ${storeCatId === cat.id ? 'active' : ''}`}
                onClick={() => { setStoreCatId(cat.id); setStorePage(1); }}
                style={{
                  backgroundColor: storeCatId === cat.id ? 'var(--primary)' : 'var(--bg-card)',
                  border: '1px solid var(--border)',
                  color: storeCatId === cat.id ? '#fff' : 'var(--text-muted)',
                  padding: '8px 16px',
                  borderRadius: '20px',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                }}
              >
                <i className="fa-solid fa-tag"></i> {cat.name}
              </button>
            ))}
          </div>

          {/* Product Cards Grid */}
          {storeLoading ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
              <i className="fa-solid fa-spinner fa-spin fa-2x" style={{ color: 'var(--primary)', marginBottom: 12 }}></i>
              <p>Đang tải danh sách sản phẩm...</p>
            </div>
          ) : storeProducts.length === 0 ? (
            <div className="card" style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
              <i className="fa-solid fa-box-open fa-3x" style={{ marginBottom: 12, opacity: 0.5 }}></i>
              <p>Không tìm thấy sản phẩm nào phù hợp.</p>
            </div>
          ) : (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 20 }}>
                {storeProducts.map((p) => {
                  const cat = categories.find((c) => c.id === p.category_id)
                  return (
                    <ProductCard
                      key={p.id}
                      product={p}
                      categoryName={cat?.name}
                      onAddToCart={handleAddToCartWithToast}
                      onViewDetail={(item) => setDetailProduct(item)}
                    />
                  )
                })}
              </div>

              <ProductPagination
                page={storePage}
                totalPages={storeTotalPages}
                total={storeTotal}
                pageSize={8}
                onPageChange={setStorePage}
              />
            </>
          )}
        </div>
      )}

      {/* 2. MÀN HÌNH QUẢN TRỊ (ADMIN BACKOFFICE) */}
      {currentPath === 'admin' && (
        <AdminLayout
          currentTab={adminTab}
          onSelectTab={setAdminTab}
          currentUser={currentUser}
          onBackToStore={() => navigate('store')}
          onOpenLogin={() => setIsAuthModalOpen(true)}
        >
          {adminTab === 'products' && (
            <ProductsPage
              categories={categories}
              showToast={showToast}
            />
          )}

          {adminTab === 'categories' && (
            <CategoriesPage
              showToast={showToast}
              onCategoryChanged={(cats) => setCategories(cats)}
            />
          )}

          {adminTab === 'users' && (
            <UsersPage
              currentUser={currentUser}
              showToast={showToast}
            />
          )}

          {adminTab === 'logs' && <ApiLogger />}
        </AdminLayout>
      )}

      {/* 3. MÀN HÌNH TRANG CÁ NHÂN (PROFILE VIEW) */}
      {currentPath === 'profile' && (
        <AuthGuard
          currentUser={currentUser}
          onOpenLogin={() => setIsAuthModalOpen(true)}
        >
          <ProfilePage
            currentUser={currentUser}
            onProfileUpdated={updateUser}
            onBackToStore={() => navigate('store')}
            onGoToAdmin={() => navigate('admin')}
            onLogout={() => {
              logout()
              navigate('store')
              showToast('Đã đăng xuất tài khoản', 'success')
            }}
            showToast={showToast}
          />
        </AuthGuard>
      )}

      {/* MODAL CHI TIẾT SẢN PHẨM */}
      {detailProduct && (
        <div className="modal-overlay" onClick={() => setDetailProduct(null)}>
          <div className="modal" style={{ maxWidth: 540 }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                <i className="fa-solid fa-circle-info" style={{ marginRight: 8, color: '#38bdf8' }}></i>
                Chi Tiết Sản Phẩm #{detailProduct.id}
              </h3>
              <button className="modal-close" onClick={() => setDetailProduct(null)}>✕</button>
            </div>

            <div style={{ padding: '10px 0' }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#fff', marginBottom: 8 }}>
                {detailProduct.name}
              </h2>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#34d399', marginBottom: 16 }}>
                {formatCurrency(detailProduct.price)}
              </div>

              <div className="card" style={{ padding: 16, backgroundColor: 'rgba(0,0,0,0.2)', marginBottom: 16 }}>
                <p style={{ color: 'var(--text-main)', lineHeight: 1.6 }}>
                  {detailProduct.description || 'Chưa có thông tin mô tả chi tiết cho sản phẩm này.'}
                </p>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                <div>Danh mục: <strong style={{ color: '#fff' }}>{categories.find((c) => c.id === detailProduct.category_id)?.name || 'Chung'}</strong></div>
                <div>Tồn kho: <strong style={{ color: '#fff' }}>{detailProduct.stock} cái</strong></div>
                <div>Trạng thái: <strong style={{ color: '#34d399' }}>Đang kinh doanh</strong></div>
                <div>Cập nhật: <strong style={{ color: '#fff' }}>{new Date(detailProduct.updated_at).toLocaleDateString('vi-VN')}</strong></div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setDetailProduct(null)}>
                Đóng
              </button>
              <button
                className="btn btn-primary"
                onClick={() => {
                  handleAddToCartWithToast(detailProduct)
                  setDetailProduct(null)
                }}
              >
                <i className="fa-solid fa-cart-plus"></i> Thêm Vào Giỏ
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL GIỎ HÀNG */}
      {isCartModalOpen && (
        <div className="modal-overlay" onClick={() => setIsCartModalOpen(false)}>
          <div className="modal" style={{ maxWidth: 540 }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                <i className="fa-solid fa-cart-shopping" style={{ marginRight: 8, color: '#38bdf8' }}></i>
                Giỏ Hàng Của Bạn ({totalItems} sản phẩm)
              </h3>
              <button className="modal-close" onClick={() => setIsCartModalOpen(false)}>✕</button>
            </div>

            {cart.length === 0 ? (
              <p style={{ textAlign: 'center', padding: '30px 0', color: 'var(--text-muted)' }}>
                Giỏ hàng của bạn đang trống.
              </p>
            ) : (
              <div>
                <div style={{ maxHeight: 280, overflowY: 'auto', marginBottom: 16 }}>
                  {cart.map(({ product, qty }) => (
                    <div
                      key={product.id}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '10px 0',
                        borderBottom: '1px solid var(--border)',
                      }}
                    >
                      <div>
                        <strong>{product.name}</strong>
                        <div style={{ color: '#34d399', fontSize: '0.85rem' }}>
                          {formatCurrency(product.price)}
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <button className="btn btn-sm btn-outline" onClick={() => updateQty(product.id, -1)}>-</button>
                        <span>{qty}</span>
                        <button className="btn btn-sm btn-outline" onClick={() => updateQty(product.id, 1)}>+</button>
                        <button
                          className="btn btn-sm btn-danger"
                          style={{ marginLeft: 8 }}
                          onClick={() => updateQty(product.id, -qty)}
                          title="Xóa"
                        >
                          <i className="fa-solid fa-trash"></i>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: 10 }}>
                  <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>Tổng thanh toán:</span>
                  <span style={{ fontSize: '1.4rem', fontWeight: 700, color: '#34d399' }}>
                    {formatCurrency(totalPrice)}
                  </span>
                </div>
              </div>
            )}

            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setIsCartModalOpen(false)}>
                Tiếp Tục Xem Hàng
              </button>
              {cart.length > 0 && (
                <button
                  className="btn btn-success"
                  onClick={() => {
                    showToast('Đặt hàng thành công (Mô phỏng)!', 'success')
                    clearCart()
                    setIsCartModalOpen(false)
                  }}
                >
                  <i className="fa-solid fa-credit-card"></i> Thanh Toán Ngay
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* MODAL ĐĂNG NHẬP / ĐĂNG KÝ */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onAuthSuccess={refreshUser}
        showToast={showToast}
      />
    </MainLayout>
  )
}
