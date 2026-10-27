import { useState } from 'react'
import Button from '../../../components/common/Button'
import ConfirmDialog from '../../../components/common/ConfirmDialog'
import Input from '../../../components/common/Input'
import Loading from '../../../components/common/Loading'
import Modal from '../../../components/common/Modal'
import ProductFilters from '../components/ProductFilters'
import ProductForm from '../components/ProductForm'
import ProductList from '../components/ProductList'
import ProductPagination from '../components/ProductPagination'
import { useProducts } from '../hooks/useProducts'
import { productService } from '../services/productService'

export default function ProductsPage({ categories = [], showToast }) {
  const {
    products,
    total,
    totalPages,
    loading,
    page,
    pageSize,
    search,
    categoryId,
    minPrice,
    maxPrice,
    sortBy,
    order,
    setPage,
    setPageSize,
    setSearch,
    setCategoryId,
    setMinPrice,
    setMaxPrice,
    setSortBy,
    setOrder,
    resetFilters,
    refetch,
  } = useProducts({ pageSize: 5 })

  // Modal Create / Edit
  const [formOpen, setFormOpen] = useState(false)
  const [editingProduct, setEditingProduct] = useState(null)
  const [formLoading, setFormLoading] = useState(false)

  // Quick Patch Modal
  const [patchProduct, setPatchProduct] = useState(null)
  const [patchPrice, setPatchPrice] = useState('')
  const [patchStock, setPatchStock] = useState('')
  const [patchLoading, setPatchLoading] = useState(false)

  // Delete Confirm Dialog
  const [deletingProduct, setDeletingProduct] = useState(null)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    setPage(1)
    refetch()
  }

  const handleCreateOpen = () => {
    setEditingProduct(null)
    setFormOpen(true)
  }

  const handleEditOpen = (p) => {
    setEditingProduct(p)
    setFormOpen(true)
  }

  const handleFormSubmit = async (data) => {
    setFormLoading(true)
    try {
      if (editingProduct) {
        await productService.update(editingProduct.id, data)
        showToast('Cập nhật sản phẩm thành công!', 'success')
      } else {
        await productService.create(data)
        showToast('Tạo sản phẩm mới thành công!', 'success')
      }
      setFormOpen(false)
      refetch()
    } catch (err) {
      showToast(err.message || 'Thao tác sản phẩm thất bại', 'error')
    } finally {
      setFormLoading(false)
    }
  }

  const handlePatchOpen = (p) => {
    setPatchProduct(p)
    setPatchPrice(p.price)
    setPatchStock(p.stock)
  }

  const handlePatchSubmit = async (e) => {
    e.preventDefault()
    setPatchLoading(true)
    try {
      const payload = {}
      if (patchPrice !== '') payload.price = parseFloat(patchPrice)
      if (patchStock !== '') payload.stock = parseInt(patchStock, 10)

      await productService.patch(patchProduct.id, payload)
      showToast(`Đã cập nhật nhanh sản phẩm #${patchProduct.id}`, 'success')
      setPatchProduct(null)
      refetch()
    } catch (err) {
      showToast(err.message || 'Lỗi cập nhật nhanh', 'error')
    } finally {
      setPatchLoading(false)
    }
  }

  const handleDeleteConfirm = async () => {
    if (!deletingProduct) return
    setDeleteLoading(true)
    try {
      await productService.delete(deletingProduct.id)
      showToast(`Đã xóa sản phẩm "${deletingProduct.name}"`, 'success')
      setDeletingProduct(null)
      refetch()
    } catch (err) {
      showToast(err.message || 'Không thể xóa sản phẩm', 'error')
    } finally {
      setDeleteLoading(false)
    }
  }

  return (
    <div className="card">
      <div className="card-title">
        <span>
          <i className="fa-solid fa-boxes-stacked" style={{ marginRight: 8, color: 'var(--accent-sky)' }}></i>
          Quản Lý Sản Phẩm Trong Kho ({total} sản phẩm)
        </span>
        <Button variant="primary" size="sm" icon="fa-solid fa-plus" onClick={handleCreateOpen}>
          Thêm Sản Phẩm Mới
        </Button>
      </div>

      {/* Filter toolbar */}
      <ProductFilters
        search={search}
        onSearchChange={setSearch}
        onSearchSubmit={handleSearchSubmit}
        categoryId={categoryId}
        onCategoryChange={(val) => { setCategoryId(val); setPage(1); }}
        minPrice={minPrice}
        onMinPriceChange={setMinPrice}
        maxPrice={maxPrice}
        onMaxPriceChange={setMaxPrice}
        sortBy={sortBy}
        onSortByChange={setSortBy}
        order={order}
        onOrderChange={setOrder}
        categories={categories}
        onReset={resetFilters}
      />

      {loading ? (
        <Loading text="Đang tải danh sách sản phẩm..." />
      ) : (
        <>
          <ProductList
            products={products}
            categories={categories}
            onEdit={handleEditOpen}
            onPatch={handlePatchOpen}
            onDelete={(p) => setDeletingProduct(p)}
          />

          <ProductPagination
            page={page}
            totalPages={totalPages}
            total={total}
            pageSize={pageSize}
            onPageChange={setPage}
            onPageSizeChange={(newSize) => { setPageSize(newSize); setPage(1); }}
          />
        </>
      )}

      {/* Modal Thêm/Sửa */}
      <ProductForm
        isOpen={formOpen}
        onClose={() => setFormOpen(false)}
        onSubmit={handleFormSubmit}
        initialData={editingProduct}
        categories={categories}
        loading={formLoading}
      />

      {/* Modal Quick Patch Giá & Kho */}
      {patchProduct && (
        <Modal
          isOpen={Boolean(patchProduct)}
          onClose={() => setPatchProduct(null)}
          title={`Cập Nhật Nhanh #${patchProduct.id}: ${patchProduct.name}`}
          icon="fa-solid fa-bolt"
          maxWidth={420}
        >
          <form onSubmit={handlePatchSubmit}>
            <Input
              label="Giá Bán Mới (VND)"
              type="number"
              required
              value={patchPrice}
              onChange={(e) => setPatchPrice(e.target.value)}
              style={{ marginBottom: 14 }}
            />
            <Input
              label="Số Lượng Tồn Kho Mới"
              type="number"
              required
              value={patchStock}
              onChange={(e) => setPatchStock(e.target.value)}
              style={{ marginBottom: 20 }}
            />
            <div className="modal-footer">
              <Button variant="outline" onClick={() => setPatchProduct(null)}>
                Hủy
              </Button>
              <Button type="submit" variant="primary" loading={patchLoading}>
                <i className="fa-solid fa-check"></i> Lưu Ngay
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* Dialog xác nhận xóa */}
      <ConfirmDialog
        isOpen={Boolean(deletingProduct)}
        onClose={() => setDeletingProduct(null)}
        onConfirm={handleDeleteConfirm}
        title="Xác nhận xóa sản phẩm"
        message={`Bạn có chắc muốn xóa sản phẩm "${deletingProduct?.name}" khỏi hệ thống? Thao tác này không thể hoàn tác.`}
        confirmText="Xóa Sản Phẩm"
        loading={deleteLoading}
      />
    </div>
  )
}
