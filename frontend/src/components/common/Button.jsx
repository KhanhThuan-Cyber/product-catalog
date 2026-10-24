export default function Button({
  children,
  variant = 'primary', // 'primary' | 'secondary' | 'success' | 'danger' | 'outline'
  size = 'md', // 'sm' | 'md'
  icon = null,
  loading = false,
  disabled = false,
  className = '',
  type = 'button',
  onClick,
  ...props
}) {
  const sizeClass = size === 'sm' ? 'btn-sm' : ''
  const variantClass = `btn-${variant}`

  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={`btn ${variantClass} ${sizeClass} ${className}`.trim()}
      onClick={onClick}
      {...props}
    >
      {loading ? (
        <i className="fa-solid fa-spinner fa-spin"></i>
      ) : icon ? (
        <i className={icon}></i>
      ) : null}
      {children}
    </button>
  )
}
