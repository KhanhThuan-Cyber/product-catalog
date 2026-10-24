import Button from '../../../components/common/Button'
import Input from '../../../components/common/Input'

export default function ProductFilters({
  search,
  onSearchChange,
  onSearchSubmit,
  categoryId,
  onCategoryChange,
  minPrice,
  onMinPriceChange,
  maxPrice,
  onMaxPriceChange,
  sortBy,
  onSortByChange,
  order,
  onOrderChange,
  categories = [],
  onReset,
}) {
  return (
    <form onSubmit={onSearchSubmit} className="filter-toolbar" style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'flex-end', marginBottom: 20 }}>
      <div style={{ flex: '1 1 200px' }}>
        <Input
          label="Tìm kiếm theo tên"
          placeholder="Nhập tên sản phẩm & Enter..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      <div className="form-group" style={{ flex: '1 1 180px' }}>
        <label>Danh mục</label>
        <select value={categoryId} onChange={(e) => onCategoryChange(e.target.value)}>
          <option value="">-- Tất cả danh mục --</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      <div style={{ flex: '0 1 130px' }}>
        <Input
          label="Giá từ"
          type="number"
          placeholder="0"
          value={minPrice}
          onChange={(e) => onMinPriceChange(e.target.value)}
        />
      </div>

      <div style={{ flex: '0 1 130px' }}>
        <Input
          label="Giá đến"
          type="number"
          placeholder="Tối đa"
          value={maxPrice}
          onChange={(e) => onMaxPriceChange(e.target.value)}
        />
      </div>

      <div className="form-group" style={{ flex: '0 1 140px' }}>
        <label>Sắp xếp theo</label>
        <select value={sortBy} onChange={(e) => onSortByChange(e.target.value)}>
          <option value="id">ID</option>
          <option value="price">Giá bán</option>
          <option value="created_at">Mới nhất</option>
          <option value="name">Tên A-Z</option>
        </select>
      </div>

      <div className="form-group" style={{ flex: '0 1 120px' }}>
        <label>Thứ tự</label>
        <select value={order} onChange={(e) => onOrderChange(e.target.value)}>
          <option value="asc">Tăng dần ↑</option>
          <option value="desc">Giảm dần ↓</option>
        </select>
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <Button type="submit" variant="primary">
          <i className="fa-solid fa-magnifying-glass"></i> Lọc
        </Button>
        {onReset && (
          <Button type="button" variant="outline" onClick={onReset} title="Khôi phục mặc định">
            <i className="fa-solid fa-rotate-left"></i>
          </Button>
        )}
      </div>
    </form>
  )
}
