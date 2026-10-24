import { useEffect, useState } from 'react'
import Button from '../../../components/common/Button'
import Input from '../../../components/common/Input'
import Modal from '../../../components/common/Modal'
import { isValidPrice, isValidStock } from '../../../utils/validators'

export default function ProductForm({
  isOpen,
  onClose,
  onSubmit,
  initialData = null,
  categories = [],
  loading = false,
}) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [price, setPrice] = useState('')
  const [stock, setStock] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (initialData) {
      setName(initialData.name || '')
      setDescription(initialData.description || '')
      setPrice(initialData.price || '')
      setStock(initialData.stock ?? 10)
      setCategoryId(initialData.category_id || categories[0]?.id || '')
    } else {
      setName('')
      setDescription('')
      setPrice('')
      setStock('10')
      setCategoryId(categories[0]?.id || '')
    }
    setErrors({})
  }, [initialData, isOpen, categories])

  const handleSubmit = (e) => {
    e.preventDefault()
    const nextErrors = {}

    if (!name.trim()) nextErrors.name = 'Vui lòng nhập tên sản phẩm'
    if (!isValidPrice(price)) nextErrors.price = 'Giá bán phải lớn hơn 0'
    if (!isValidStock(stock)) nextErrors.stock = 'Tồn kho không được âm'
    if (!categoryId) nextErrors.category = 'Vui lòng chọn danh mục'

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors)
      return
    }

    setErrors({})
    onSubmit({
      name: name.trim(),
      description: description.trim() || null,
      price: parseFloat(price),
      stock: parseInt(stock, 10),
      category_id: parseInt(categoryId, 10),
    })
  }

  const isEdit = Boolean(initialData)

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? `Cập Nhật Sản Phẩm #${initialData?.id}` : 'Thêm Sản Phẩm Mới'}
      icon={isEdit ? 'fa-solid fa-pen-to-square' : 'fa-solid fa-box-open'}
      maxWidth={500}
    >
      <form onSubmit={handleSubmit}>
        <Input
          label="Tên Sản Phẩm"
          required
          placeholder="Nhập tên sản phẩm..."
          value={name}
          onChange={(e) => setName(e.target.value)}
          error={errors.name}
          style={{ marginBottom: 14 }}
        />

        <div className="form-group" style={{ marginBottom: 14 }}>
          <label>Mô Tả Sản Phẩm</label>
          <textarea
            rows={3}
            placeholder="Mô tả thông số hoặc tính năng nổi bật..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
          <Input
            label="Giá Bán (VND)"
            type="number"
            required
            placeholder="150000"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            error={errors.price}
          />
          <Input
            label="Tồn Kho"
            type="number"
            required
            placeholder="10"
            value={stock}
            onChange={(e) => setStock(e.target.value)}
            error={errors.stock}
          />
        </div>

        <div className="form-group" style={{ marginBottom: 20 }}>
          <label>Danh Mục *</label>
          <select
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
            required
          >
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          {errors.category && (
            <small style={{ color: 'var(--danger)', fontSize: '0.75rem' }}>{errors.category}</small>
          )}
        </div>

        <div className="modal-footer">
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Hủy
          </Button>
          <Button type="submit" variant="primary" loading={loading}>
            <i className="fa-solid fa-check"></i>
            {isEdit ? 'Lưu Sản Phẩm' : 'Tạo Sản Phẩm'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
