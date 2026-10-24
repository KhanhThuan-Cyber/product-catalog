export default function Breadcrumbs({ items = [] }) {
  if (!items || items.length === 0) return null

  return (
    <nav className="breadcrumbs" aria-label="breadcrumb">
      {items.map((item, index) => {
        const isLast = index === items.length - 1
        return (
          <span key={index} style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
            {index > 0 && <span className="crumb-separator">/</span>}
            {isLast ? (
              <span className="crumb-current">{item.label}</span>
            ) : (
              <span
                className="crumb-link"
                onClick={item.onClick}
                role="button"
                tabIndex={0}
              >
                {item.icon && <i className={item.icon} style={{ marginRight: 4 }}></i>}
                {item.label}
              </span>
            )}
          </span>
        )
      })}
    </nav>
  )
}
