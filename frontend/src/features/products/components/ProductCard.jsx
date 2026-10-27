import { useState } from 'react'
import Button from '../../../components/common/Button'
import { formatCurrency } from '../../../utils/formatCurrency'

export default function ProductCard({
  product,
  categoryName,
  onAddToCart,
  onViewDetail,
}) {
  const isOutOfStock = product.stock <= 0
  const [imgError, setImgError] = useState(false)

  return (
    <div className="product-card">
      {/* Thumbnail */}
      <div
        className="card-thumb"
        onClick={() => onViewDetail && onViewDetail(product)}
        style={{ cursor: 'pointer' }}
      >
        {product.image_url && !imgError ? (
          <img
            src={product.image_url}
            alt={product.name}
            onError={() => setImgError(true)}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              display: 'block',
            }}
          />
        ) : (
          <i className="fa-solid fa-laptop placeholder-icon"></i>
        )}
        {categoryName && (
          <span className="card-cat-badge badge badge-active">
            {categoryName}
          </span>
        )}
      </div>

      <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', flex: 1 }}>
        <h4
          style={{
            fontSize: '1.05rem',
            fontWeight: 600,
            marginBottom: 6,
            cursor: 'pointer',
            display: '-webkit-box',
            WebkitLineClamp: 1,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}
          onClick={() => onViewDetail && onViewDetail(product)}
        >
          {product.name}
        </h4>

        <p
          style={{
            fontSize: '0.85rem',
            color: 'var(--text-muted)',
            marginBottom: 12,
            flex: 1,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}
        >
          {product.description || 'Chưa có thông tin mô tả chi tiết cho sản phẩm này.'}
        </p>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
          <span style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-emerald)' }}>
            {formatCurrency(product.price)}
          </span>
          <span style={{ fontSize: '0.75rem', color: isOutOfStock ? 'var(--accent-red)' : 'var(--text-muted)' }}>
            {isOutOfStock ? 'Hết hàng' : `Kho: ${product.stock}`}
          </span>
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          {onViewDetail && (
            <Button
              size="sm"
              variant="outline"
              style={{ flex: 1 }}
              onClick={() => onViewDetail(product)}
            >
              Chi Tiết
            </Button>
          )}
          {onAddToCart && (
            <Button
              size="sm"
              variant="primary"
              disabled={isOutOfStock}
              style={{ flex: 1 }}
              onClick={() => onAddToCart(product)}
            >
              <i className="fa-solid fa-cart-plus"></i> Chọn Mua
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
