import { useCallback, useEffect, useState } from 'react'
import { productService } from '../services/productService'

export function useProducts(initialParams = {}) {
  const [products, setProducts] = useState([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Query & Filter params
  const [page, setPage] = useState(initialParams.page || 1)
  const [pageSize, setPageSize] = useState(initialParams.pageSize || 10)
  const [search, setSearch] = useState(initialParams.search || '')
  const [categoryId, setCategoryId] = useState(initialParams.categoryId || '')
  const [minPrice, setMinPrice] = useState(initialParams.minPrice || '')
  const [maxPrice, setMaxPrice] = useState(initialParams.maxPrice || '')
  const [sortBy, setSortBy] = useState(initialParams.sortBy || 'id')
  const [order, setOrder] = useState(initialParams.order || 'asc')

  const fetchProducts = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = {
        page,
        page_size: pageSize,
        sort_by: sortBy,
        order,
      }
      if (search.trim()) params.search = search.trim()
      if (categoryId) params.category_id = categoryId
      if (minPrice) params.min_price = minPrice
      if (maxPrice) params.max_price = maxPrice

      const res = await productService.listPaginated(params)
      setProducts(res?.items || [])
      setTotal(res?.total || 0)
      setTotalPages(res?.total_pages || 0)
    } catch (err) {
      setError(err.message || 'Lỗi tải danh sách sản phẩm')
    } finally {
      setLoading(false)
    }
  }, [page, pageSize, search, categoryId, minPrice, maxPrice, sortBy, order])

  useEffect(() => {
    fetchProducts()
  }, [fetchProducts])

  const resetFilters = () => {
    setSearch('')
    setCategoryId('')
    setMinPrice('')
    setMaxPrice('')
    setSortBy('id')
    setOrder('asc')
    setPage(1)
  }

  return {
    products,
    total,
    totalPages,
    loading,
    error,
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
    refetch: fetchProducts,
  }
}
