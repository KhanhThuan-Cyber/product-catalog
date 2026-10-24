export default function Modal({
  isOpen,
  onClose,
  title,
  icon,
  children,
  maxWidth = 520,
}) {
  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal"
        style={{ maxWidth }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>
            {icon && <i className={icon} style={{ marginRight: 8 }}></i>}
            {title}
          </h3>
          <button className="modal-close" onClick={onClose} title="Đóng">
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}
