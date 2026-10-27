import Button from '../../../components/common/Button'

export default function CategoryList({
  categories = [],
  onEdit,
  onDelete,
}) {
  if (categories.length === 0) {
    return (
      <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '30px 0' }}>
        Chưa có danh mục nào. Hãy tạo danh mục đầu tiên!
      </p>
    )
  }

  return (
    <div className="table-responsive">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Tên Danh Mục</th>
            <th>Mô Tả</th>
            <th>Ngày Tạo</th>
            <th>Thao Tác</th>
          </tr>
        </thead>
        <tbody>
          {categories.map((c) => (
            <tr key={c.id}>
              <td><strong>#{c.id}</strong></td>
              <td>
                <span style={{ fontWeight: 600, color: 'var(--accent-sky)' }}>
                  <i className="fa-solid fa-folder" style={{ marginRight: 6 }}></i>
                  {c.name}
                </span>
              </td>
              <td style={{ color: 'var(--text-muted)' }}>{c.description || '—'}</td>
              <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                {c.created_at ? new Date(c.created_at).toLocaleDateString('vi-VN') : '—'}
              </td>
              <td>
                <div style={{ display: 'flex', gap: 8 }}>
                  <Button
                    size="sm"
                    variant="secondary"
                    icon="fa-solid fa-pen"
                    onClick={() => onEdit(c)}
                  >
                    Sửa
                  </Button>
                  <Button
                    size="sm"
                    variant="danger"
                    icon="fa-solid fa-trash"
                    onClick={() => onDelete(c)}
                  >
                    Xóa
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
