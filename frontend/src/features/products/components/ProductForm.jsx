import { useEffect, useState } from 'react'
import Button from '../../../components/common/Button'
import Input from '../../../components/common/Input'
import Modal from '../../../components/common/Modal'
import { isValidImageUrl, isValidPrice, isValidStock } from '../../../utils/validators'

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
  const [imageUrl, setImageUrl] = useState('')
  const [imagePreviewError, setImagePreviewError] = useState(false)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (initialData) {
      setName(initialData.name || '')
      setDescription(initialData.description || '')
      setPrice(initialData.price || '')
      setStock(initialData.stock ?? 10)
      setCategoryId(initialData.category_id || categories[0]?.id || '')
      setImageUrl(initialData.image_url || '')
    } else {
      setName('')
      setDescription('')
      setPrice('')
      setStock('10')
      setCategoryId(categories[0]?.id || '')
      setImageUrl('')
    }
    setImagePreviewError(false)
    setErrors({})
  }, [initialData, isOpen, categories])

  const handleSubmit = (e) => {
    e.preventDefault()
    const nextErrors = {}

    if (!name.trim()) nextErrors.name = 'Vui lòng nhập tên sản phẩm'
    if (!isValidPrice(price)) nextErrors.price = 'Giá bán phải lớn hơn 0'
    if (!isValidStock(stock)) nextErrors.stock = 'Tồn kho không được âm'
    if (!categoryId) nextErrors.category = 'Vui lòng chọn danh mục'
    if (!isValidImageUrl(imageUrl)) nextErrors.imageUrl = 'URL ảnh không hợp lệ (phải bắt đầu bằng http/https, tối đa 500 ký tự)'

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
      image_url: imageUrl.trim() || null,
    })
  }

  const isEdit = Boolean(initialData)
  const showPreview = imageUrl.trim() && !imagePreviewError

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

        <div className="form-group" style={{ marginBottom: 14 }}>
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

        {/* Image URL input + preview */}
        <div className="form-group" style={{ marginBottom: 20 }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <i className="fa-solid fa-image" style={{ color: '#60a5fa' }}></i>
            URL Hình Ảnh
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 400 }}>(tuỳ chọn)</span>
          </label>
          <input
            type="url"
            placeholder="https://example.com/image.jpg"
            value={imageUrl}
            onChange={(e) => {
              setImageUrl(e.target.value)
              setImagePreviewError(false)
            }}
            style={{ width: '100%' }}
          />
          {errors.imageUrl && (
            <small style={{ color: 'var(--danger)', fontSize: '0.75rem' }}>{errors.imageUrl}</small>
          )}

          {/* Live preview */}
          {showPreview && (
            <div style={{
              marginTop: 10,
              borderRadius: 8,
              overflow: 'hidden',
              border: '1px solid var(--border)',
              background: 'var(--bg-card-secondary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: 140,
            }}>
              <img
                src={imageUrl.trim()}
                alt="Preview"
                onError={() => setImagePreviewError(true)}
                style={{ maxHeight: 140, maxWidth: '100%', objectFit: 'contain' }}
              />
            </div>
          )}
          {imageUrl.trim() && imagePreviewError && (
            <div style={{
              marginTop: 10,
              borderRadius: 8,
              border: '1px dashed var(--border)',
              background: 'var(--bg-card-secondary)',
              height: 80,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              color: 'var(--text-muted)',
              fontSize: '0.85rem',
            }}>
              <i className="fa-solid fa-image-slash"></i>
              Không thể tải ảnh từ URL này
            </div>
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
