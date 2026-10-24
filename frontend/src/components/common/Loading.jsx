export default function Loading({ text = 'Đang tải dữ liệu...' }) {
  return (
    <div style={{ textAlign: 'center', padding: '36px 0', color: 'var(--text-muted)' }}>
      <i
        className="fa-solid fa-spinner fa-spin fa-2x"
        style={{ color: 'var(--primary)', marginBottom: 12, display: 'block' }}
      ></i>
      <p style={{ fontSize: '0.9rem' }}>{text}</p>
    </div>
  )
}
