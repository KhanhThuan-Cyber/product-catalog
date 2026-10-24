import Button from './Button'
import Modal from './Modal'

export default function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title = 'Xác nhận thao tác',
  message = 'Bạn có chắc chắn muốn thực hiện hành động này?',
  confirmText = 'Xác Nhận',
  cancelText = 'Hủy Bỏ',
  confirmVariant = 'danger',
  loading = false,
}) {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      icon="fa-solid fa-triangle-exclamation"
      maxWidth={440}
    >
      <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginBottom: 20 }}>
        {message}
      </p>

      <div className="modal-footer">
        <Button variant="outline" onClick={onClose} disabled={loading}>
          {cancelText}
        </Button>
        <Button
          variant={confirmVariant}
          onClick={onConfirm}
          loading={loading}
        >
          {confirmText}
        </Button>
      </div>
    </Modal>
  )
}
