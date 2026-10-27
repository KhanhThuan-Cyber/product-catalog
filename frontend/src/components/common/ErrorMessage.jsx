export default function ErrorMessage({ message, onRetry }) {
  if (!message) return null

  return (
    <div
      style={{
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        border: '1px solid var(--danger)',
        borderRadius: 'var(--radius)',
        padding: '16px 20px',
        color: 'var(--accent-red)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        margin: '16px 0',
        gap: 12,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <i className="fa-solid fa-circle-exclamation" style={{ color: 'var(--danger)' }}></i>
        <span>{message}</span>
      </div>
      {onRetry && (
        <button
          className="btn btn-sm btn-outline"
          onClick={onRetry}
          style={{ borderColor: 'var(--danger)', color: 'var(--accent-red)' }}
        >
          <i className="fa-solid fa-arrows-rotate"></i> Thử lại
        </button>
      )}
    </div>
  )
}
