import { useEffect, useState } from 'react'
import { api } from '../api/client'

function ProductImage({ src, alt, className, style }) {
  const [error, setError] = useState(false)
  if (!src || error) {
    return (
      <div className={className} style={{ ...style, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <i className="fa-solid fa-cube placeholder-icon"></i>
      </div>
    )
  }
  return (
    <img
      src={src}
      alt={alt}
      className={className}
      onError={() => setError(true)}
      style={{ ...style, objectFit: 'cover', width: '100%', height: '100%' }}
    />
  )
}

export default function StorefrontView({ categories, onAddToCart, showToast }) {
  const [products, setProducts] = useState([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [loading, setLoading] = useState(false)

  // Filters
  const [search, setSearch] = useState('')
  const [selectedCatId, setSelectedCatId] = useState('')
  const [minPrice, setMinPrice] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const [sortBy, setSortBy] = useState('created_at')
  const [order, setOrder] = useState('desc')
  const [page, setPage] = useState(1)
  const pageSize = 8

  // Modal xem chi tiết
  const [viewProduct, setViewProduct] = useState(null)

  const fetchProducts = async () => {
    setLoading(true)
    try {
      const params = {
        page,
        page_size: pageSize,
        sort_by: sortBy,
        order,
      }
      if (search.trim()) params.search = search.trim()
      if (selectedCatId) params.category_id = selectedCatId
      if (minPrice) params.min_price = minPrice
      if (maxPrice) params.max_price = maxPrice

      const res = await api.get('/products', params)
      setProducts(res?.items || [])
      setTotal(res?.total || 0)
      setTotalPages(res?.total_pages || 0)
    } catch (err) {
      showToast(err.message || 'Lỗi tải sản phẩm', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProducts()
  }, [page, selectedCatId, sortBy, order])

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    setPage(1)
    fetchProducts()
  }

  const handleReset = () => {
    setSearch('')
    setSelectedCatId('')
    setMinPrice('')
    setMaxPrice('')
    setSortBy('created_at')
    setOrder('desc')
    setPage(1)
  }

  const formatCurrency = (val) => {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val)
  }

  return (
    <div className="storefront">
      {/* Hero Banner */}
      <div className="hero-banner">
        <div className="hero-content">
          <h2>
            <i className="fa-solid fa-store" style={{ marginRight: 10, color: '#60a5fa' }}></i>
            Chào mừng đến với Cửa Hàng Trực Tuyến
          </h2>
          <p>Khám phá hàng loạt sản phẩm công nghệ, linh kiện và phụ kiện chính hãng giá ưu đãi nhất.</p>

          <form onSubmit={handleSearchSubmit} className="hero-search-box">
            <i className="fa-solid fa-magnifying-glass search-icon"></i>
            <input
              type="text"
              placeholder="Tìm kiếm sản phẩm theo tên (ví dụ: Chuột, Bàn phím, Tai nghe...)"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <button type="submit" className="btn btn-primary">
              Tìm Kiếm
            </button>
          </form>
        </div>
      </div>

      {/* Danh mục nhanh (Category Pills) */}
      <div className="category-chips-bar">
        <button
          className={`chip-btn ${selectedCatId === '' ? 'active' : ''}`}
          onClick={() => { setSelectedCatId(''); setPage(1); }}
        >
          <i className="fa-solid fa-layer-group"></i> Tất Cả
        </button>
        {categories.map((c) => (
          <button
            key={c.id}
            className={`chip-btn ${selectedCatId === String(c.id) ? 'active' : ''}`}
            onClick={() => { setSelectedCatId(String(c.id)); setPage(1); }}
          >
            <i className="fa-solid fa-tag"></i> {c.name}
          </button>
        ))}
      </div>

      {/* Thanh lọc nâng cao & Sắp xếp */}
      <div className="store-filter-bar">
        <div className="filter-left">
          <div className="filter-input-wrap">
            <i className="fa-solid fa-filter"></i>
            <span>Khoảng giá:</span>
            <input
              type="number"
              placeholder="Giá từ..."
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
              className="price-input"
            />
            <span>—</span>
            <input
              type="number"
              placeholder="Giá đến..."
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              className="price-input"
            />
            <button className="btn btn-sm btn-secondary" onClick={() => { setPage(1); fetchProducts(); }}>
              Áp dụng
            </button>
            {(minPrice || maxPrice || search || selectedCatId) && (
              <button className="btn btn-sm btn-outline" onClick={handleReset}>
                <i className="fa-solid fa-xmark"></i> Xóa lọc
              </button>
            )}
          </div>
        </div>

        <div className="filter-right">
          <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            <i className="fa-solid fa-arrow-down-wide-short"></i> Sắp xếp:
          </label>
          <select
            value={`${sortBy}-${order}`}
            onChange={(e) => {
              const [f, o] = e.target.value.split('-')
              setSortBy(f)
              setOrder(o)
              setPage(1)
            }}
          >
            <option value="created_at-desc">Mới nhất</option>
            <option value="price-asc">Giá: Thấp đến Cao</option>
            <option value="price-desc">Giá: Cao đến Thấp</option>
            <option value="name-asc">Tên: A - Z</option>
          </select>
        </div>
      </div>

      {/* Lưới sản phẩm (Product Grid Cards) */}
      <div className="products-grid-section">
        {loading ? (
          <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
            <i className="fa-solid fa-circle-notch fa-spin fa-2x"></i>
            <p style={{ marginTop: 12 }}>Đang tải danh sách sản phẩm...</p>
          </div>
        ) : products.length === 0 ? (
          <div className="empty-box">
            <i className="fa-solid fa-box-open fa-3x" style={{ color: '#475569' }}></i>
            <h3>Không tìm thấy sản phẩm nào</h3>
            <p>Hãy thử tìm kiếm với từ khóa khác hoặc điều chỉnh khoảng giá lọc.</p>
            <button className="btn btn-outline" onClick={handleReset} style={{ marginTop: 12 }}>
              Xem toàn bộ sản phẩm
            </button>
          </div>
        ) : (
          <div className="product-cards-grid">
            {products.map((p) => {
              const catName = categories.find((c) => c.id === p.category_id)?.name || 'Sản phẩm'
              return (
                <div key={p.id} className="product-card">
                  <div className="card-thumb" onClick={() => setViewProduct(p)} style={{ cursor: 'pointer' }}>
                    <ProductImage
                      src={p.image_url}
                      alt={p.name}
                      style={{ borderRadius: 'inherit' }}
                    />
                    <span className="card-cat-badge">{catName}</span>
                  </div>

                  <div className="card-body">
                    <h4 className="product-title" title={p.name}>{p.name}</h4>
                    <p className="product-desc">{p.description || 'Chưa có mô tả chi tiết.'}</p>

                    <div className="product-price-row">
                      <div className="price-tag">{formatCurrency(p.price)}</div>
                      <div className="stock-info">
                        {p.stock > 0 ? (
                          <span style={{ color: '#34d399' }}>
                            <i className="fa-solid fa-check"></i> Còn {p.stock}
                          </span>
                        ) : (
                          <span style={{ color: '#f87171' }}>
                            <i className="fa-solid fa-xmark"></i> Hết hàng
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="card-actions">
                      <button
                        className="btn btn-sm btn-outline"
                        style={{ flex: 1 }}
                        onClick={() => setViewProduct(p)}
                      >
                        <i className="fa-regular fa-eye"></i> Chi tiết
                      </button>
                      <button
                        className="btn btn-sm btn-primary"
                        style={{ flex: 1 }}
                        disabled={p.stock <= 0}
                        onClick={() => onAddToCart(p)}
                      >
                        <i className="fa-solid fa-cart-plus"></i> Chọn mua
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Phân trang Trang chủ */}
      {totalPages > 1 && (
        <div className="pagination-bar" style={{ marginTop: 28, justifyContent: 'center' }}>
          <div className="pagination-controls">
            <button
              className="btn btn-sm btn-outline"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              <i className="fa-solid fa-chevron-left"></i> Trang trước
            </button>

            <span style={{ padding: '0 12px', fontSize: '0.9rem' }}>
              Trang <strong>{page}</strong> / <strong>{totalPages}</strong>
            </span>

            <button
              className="btn btn-sm btn-outline"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              Trang sau <i className="fa-solid fa-chevron-right"></i>
            </button>
          </div>
        </div>
      )}

      {/* Modal Xem chi tiết sản phẩm */}
      {viewProduct && (
        <div className="modal-overlay">
          <div className="modal" style={{ maxWidth: 520 }}>
            <div className="modal-header">
              <h3>
                <i className="fa-solid fa-box" style={{ marginRight: 8, color: '#60a5fa' }}></i>
                Chi Tiết Sản Phẩm #{viewProduct.id}
              </h3>
              <button className="modal-close" onClick={() => setViewProduct(null)}>✕</button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {/* Ảnh sản phẩm trong modal chi tiết */}
              {viewProduct.image_url && (
                <div style={{
                  borderRadius: 8,
                  overflow: 'hidden',
                  border: '1px solid var(--border)',
                  background: 'var(--bg-card-secondary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: 200,
                }}>
                  <img
                    src={viewProduct.image_url}
                    alt={viewProduct.name}
                    style={{ maxHeight: 200, maxWidth: '100%', objectFit: 'contain' }}
                    onError={(e) => { e.currentTarget.parentElement.style.display = 'none' }}
                  />
                </div>
              )}
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff' }}>
                {viewProduct.name}
              </div>
              <div>
                <span className="badge badge-category">
                  {categories.find((c) => c.id === viewProduct.category_id)?.name || 'Danh mục'}
                </span>
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#34d399' }}>
                {formatCurrency(viewProduct.price)}
              </div>
              <div style={{ background: 'var(--bg-card-secondary)', padding: 12, borderRadius: 6, fontSize: '0.9rem' }}>
                <strong>Mô tả:</strong>
                <p style={{ marginTop: 4, color: 'var(--text-main)' }}>
                  {viewProduct.description || 'Chưa có thông tin mô tả chi tiết cho sản phẩm này.'}
                </p>
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                <div><i className="fa-solid fa-warehouse"></i> Tồn kho: <strong>{viewProduct.stock} cái</strong></div>
                <div><i className="fa-solid fa-calendar"></i> Ngày đăng: {new Date(viewProduct.created_at).toLocaleString('vi-VN')}</div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setViewProduct(null)}>
                Đóng
              </button>
              <button
                className="btn btn-primary"
                disabled={viewProduct.stock <= 0}
                onClick={() => {
                  onAddToCart(viewProduct)
                  setViewProduct(null)
                }}
              >
                <i className="fa-solid fa-cart-plus"></i> Thêm Vào Giỏ Hàng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
