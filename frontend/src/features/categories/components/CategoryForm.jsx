import { useEffect, useState } from 'react'
import Button from '../../../components/common/Button'
import Input from '../../../components/common/Input'
import Modal from '../../../components/common/Modal'

export default function CategoryForm({
  isOpen,
  onClose,
  onSubmit,
  initialData = null,
  loading = false,
}) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  useEffect(() => {
    if (initialData) {
      setName(initialData.name || '')
      setDescription(initialData.description || '')
    } else {
      setName('')
      setDescription('')
    }
  }, [initialData, isOpen])

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      name: name.trim(),
      description: description.trim() || null,
    })
  }

  const isEdit = Boolean(initialData)

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? 'Cập Nhật Danh Mục' : 'Thêm Danh Mục Mới'}
      icon={isEdit ? 'fa-solid fa-pen-to-square' : 'fa-solid fa-folder-plus'}
      maxWidth={460}
    >
      <form onSubmit={handleSubmit}>
        <Input
          label="Tên Danh Mục"
          required
          placeholder="Ví dụ: Laptop, Smartphone, Phụ kiện..."
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ marginBottom: 14 }}
        />

        <div className="form-group" style={{ marginBottom: 20 }}>
          <label>Mô Tả Danh Mục</label>
          <textarea
            rows={3}
            placeholder="Mô tả tóm tắt cho nhóm danh mục..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <div className="modal-footer">
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Hủy
          </Button>
          <Button type="submit" variant="primary" loading={loading}>
            <i className="fa-solid fa-check"></i>
            {isEdit ? 'Lưu Thay Đổi' : 'Tạo Danh Mục'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
