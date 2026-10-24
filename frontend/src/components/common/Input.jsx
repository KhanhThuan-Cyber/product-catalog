export default function Input({
  label,
  error,
  helperText,
  id,
  type = 'text',
  className = '',
  required = false,
  ...props
}) {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined)

  return (
    <div className={`form-group ${className}`.trim()}>
      {label && (
        <label htmlFor={inputId}>
          {label} {required && <span style={{ color: 'var(--danger)' }}>*</span>}
        </label>
      )}
      <input
        id={inputId}
        type={type}
        required={required}
        style={error ? { borderColor: 'var(--danger)' } : {}}
        {...props}
      />
      {error ? (
        <small style={{ color: 'var(--danger)', fontSize: '0.75rem' }}>{error}</small>
      ) : helperText ? (
        <small style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{helperText}</small>
      ) : null}
    </div>
  )
}
