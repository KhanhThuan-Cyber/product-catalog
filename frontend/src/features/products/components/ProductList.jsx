import Button from '../../../components/common/Button'
import { formatCurrency } from '../../../utils/formatCurrency'

export default function ProductList({
  products = [],
  categories = [],
  onEdit,
  onPatch,
  onDelete,
}) {
  if (products.length === 0) {
    return (
      <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '36px 0' }}>
        Không tìm thấy sản phẩm nào phù hợp với bộ lọc hiện tại.
      </p>
    )
  }

  const getCatName = (catId) => {
    return categories.find((c) => c.id === catId)?.name || `Cat #${catId}`
  }

  return (
    <div className="table-responsive">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Tên Sản Phẩm</th>
            <th>Danh Mục</th>
            <th>Giá Bán</th>
            <th>Tồn Kho</th>
            <th>Trạng Thái</th>
            <th>Thao Tác</th>
          </tr>
        </thead>
        <tbody>
          {products.map((p) => {
            const isOutOfStock = p.stock <= 0
            return (
              <tr key={p.id}>
                <td><strong>#{p.id}</strong></td>
                <td>
                  <div>
                    <strong style={{ color: '#f8fafc' }}>{p.name}</strong>
                    {p.description && (
                      <div
                        style={{
                          color: 'var(--text-muted)',
                          fontSize: '0.8rem',
                          maxWidth: 320,
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                        }}
                      >
                        {p.description}
                      </div>
                    )}
                  </div>
                </td>
                <td>
                  <span className="badge badge-active">
                    <i className="fa-solid fa-folder" style={{ marginRight: 4 }}></i>
                    {getCatName(p.category_id)}
                  </span>
                </td>
                <td>
                  <span style={{ fontWeight: 600, color: '#34d399' }}>
                    {formatCurrency(p.price)}
                  </span>
                </td>
                <td>
                  <span style={{ color: isOutOfStock ? '#ef4444' : 'var(--text-main)', fontWeight: isOutOfStock ? 700 : 400 }}>
                    {p.stock}
                  </span>
                </td>
                <td>
                  <span className={`badge ${p.is_active ? 'badge-active' : 'badge-inactive'}`}>
                    <i className={p.is_active ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-xmark'} style={{ marginRight: 4 }}></i>
                    {p.is_active ? 'Kinh doanh' : 'Tạm ẩn'}
                  </span>
                </td>
                <td>
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {onPatch && (
                      <Button
                        size="sm"
                        variant="outline"
                        title="Cập nhật nhanh Giá / Tồn kho"
                        onClick={() => onPatch(p)}
                      >
                        <i className="fa-solid fa-bolt"></i> Nhanh
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => onEdit(p)}
                      title="Sửa toàn bộ"
                    >
                      <i className="fa-solid fa-pen"></i> Sửa
                    </Button>
                    <Button
                      size="sm"
                      variant="danger"
                      onClick={() => onDelete(p)}
                      title="Xóa sản phẩm"
                    >
                      <i className="fa-solid fa-trash"></i>
                    </Button>
                  </div>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
