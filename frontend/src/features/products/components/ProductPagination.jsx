export default function ProductPagination({
  page,
  totalPages,
  total,
  pageSize,
  onPageChange,
  onPageSizeChange,
}) {
  if (total === 0) return null

  const start = (page - 1) * pageSize + 1
  const end = Math.min(page * pageSize, total)

  return (
    <div className="pagination">
      <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        Hiển thị <strong>{start}–{end}</strong> trên tổng số <strong>{total}</strong> sản phẩm
      </div>

      <div className="pagination-controls">
        {onPageSizeChange && (
          <select
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            style={{ marginRight: 12, padding: '4px 8px' }}
          >
            <option value={5}>5 / trang</option>
            <option value={10}>10 / trang</option>
            <option value={20}>20 / trang</option>
            <option value={50}>50 / trang</option>
          </select>
        )}

        <button
          className="page-btn"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          title="Trang trước"
        >
          <i className="fa-solid fa-chevron-left"></i>
        </button>

        <span style={{ fontSize: '0.9rem', padding: '0 8px' }}>
          Trang <strong>{page}</strong> / {totalPages || 1}
        </span>

        <button
          className="page-btn"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
          title="Trang tiếp"
        >
          <i className="fa-solid fa-chevron-right"></i>
        </button>
      </div>
    </div>
  )
}
