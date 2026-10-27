export default function AuthLayout({ children, title, subtitle }) {
  return (
    <div
      style={{
        minHeight: '70vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 20,
      }}
    >
      <div className="card" style={{ maxWidth: 440, width: '100%', padding: '32px 28px' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <i className="fa-solid fa-cube fa-2x" style={{ color: 'var(--accent-sky)', marginBottom: 8 }}></i>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-heading)' }}>{title}</h2>
          {subtitle && (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>
              {subtitle}
            </p>
          )}
        </div>
        {children}
      </div>
    </div>
  )
}
