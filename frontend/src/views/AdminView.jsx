import { useState } from 'react'
import ApiLogger from '../components/ApiLogger'
import CategoriesPage from '../features/categories/pages/CategoriesPage'
import ProductsPage from '../features/products/pages/ProductsPage'
import UsersPage from '../features/users/pages/UsersPage'
import AdminLayout from '../layouts/AdminLayout'

export default function AdminView({
  currentUser,
  categories,
  onCategoryChanged,
  onBackToStore,
  onOpenLogin,
  showToast,
}) {
  const [adminTab, setAdminTab] = useState('products')

  return (
    <AdminLayout
      currentTab={adminTab}
      onSelectTab={setAdminTab}
      currentUser={currentUser}
      onBackToStore={onBackToStore}
      onOpenLogin={onOpenLogin}
    >
      {adminTab === 'products' && (
        <ProductsPage categories={categories} showToast={showToast} />
      )}
      {adminTab === 'categories' && (
        <CategoriesPage showToast={showToast} onCategoryChanged={onCategoryChanged} />
      )}
      {adminTab === 'users' && (
        <UsersPage currentUser={currentUser} showToast={showToast} />
      )}
      {adminTab === 'logs' && <ApiLogger />}
    </AdminLayout>
  )
}
