import { useEffect, useState } from 'react'
import Button from '../../../components/common/Button'
import ConfirmDialog from '../../../components/common/ConfirmDialog'
import Loading from '../../../components/common/Loading'
import CategoryForm from '../components/CategoryForm'
import CategoryList from '../components/CategoryList'
import { categoryService } from '../services/categoryService'

export default function CategoriesPage({ showToast, onCategoryChanged }) {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [formOpen, setFormOpen] = useState(false)
  const [editingCategory, setEditingCategory] = useState(null)
  const [formLoading, setFormLoading] = useState(false)

  // Dialog xóa
  const [deletingCategory, setDeletingCategory] = useState(null)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const fetchCategories = async () => {
    setLoading(true)
    try {
      const data = await categoryService.list()
      setCategories(data || [])
      if (onCategoryChanged) onCategoryChanged(data || [])
    } catch (err) {
      showToast(err.message || 'Lỗi tải danh mục', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCategories()
  }, [])

  const handleCreateOpen = () => {
    setEditingCategory(null)
    setFormOpen(true)
  }

  const handleEditOpen = (cat) => {
    setEditingCategory(cat)
    setFormOpen(true)
  }

  const handleFormSubmit = async (data) => {
    setFormLoading(true)
    try {
      if (editingCategory) {
        await categoryService.update(editingCategory.id, data)
        showToast('Cập nhật danh mục thành công!', 'success')
      } else {
        await categoryService.create(data)
        showToast('Tạo danh mục mới thành công!', 'success')
      }
      setFormOpen(false)
      fetchCategories()
    } catch (err) {
      showToast(err.message || 'Thao tác thất bại', 'error')
    } finally {
      setFormLoading(false)
    }
  }

  const handleDeleteConfirm = async () => {
    if (!deletingCategory) return
    setDeleteLoading(true)
    try {
      await categoryService.delete(deletingCategory.id)
      showToast(`Đã xóa danh mục "${deletingCategory.name}"`, 'success')
      setDeletingCategory(null)
      fetchCategories()
    } catch (err) {
      showToast(err.message || 'Không thể xóa danh mục', 'error')
    } finally {
      setDeleteLoading(false)
    }
  }

  return (
    <div className="card">
      <div className="card-title">
        <span>
          <i className="fa-solid fa-folder-tree" style={{ marginRight: 8, color: 'var(--accent-sky)' }}></i>
          Quản Lý Danh Mục Sản Phẩm ({categories.length})
        </span>
        <Button variant="primary" size="sm" icon="fa-solid fa-plus" onClick={handleCreateOpen}>
          Thêm Danh Mục
        </Button>
      </div>

      {loading ? (
        <Loading text="Đang tải danh mục..." />
      ) : (
        <CategoryList
          categories={categories}
          onEdit={handleEditOpen}
          onDelete={(cat) => setDeletingCategory(cat)}
        />
      )}

      {/* Form modal */}
      <CategoryForm
        isOpen={formOpen}
        onClose={() => setFormOpen(false)}
        onSubmit={handleFormSubmit}
        initialData={editingCategory}
        loading={formLoading}
      />

      {/* Dialog xác nhận xóa */}
      <ConfirmDialog
        isOpen={Boolean(deletingCategory)}
        onClose={() => setDeletingCategory(null)}
        onConfirm={handleDeleteConfirm}
        title="Xác nhận xóa danh mục"
        message={`Bạn có chắc muốn xóa danh mục "${deletingCategory?.name}"? Lưu ý: Không thể xóa danh mục nếu đang có sản phẩm thuộc danh mục này.`}
        confirmText="Xóa Danh Mục"
        loading={deleteLoading}
      />
    </div>
  )
}
