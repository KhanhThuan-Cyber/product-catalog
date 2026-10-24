export default function Sidebar({
  currentTab,
  onSelectTab,
  tabs = [
    { id: 'products', label: 'Quản Lý Sản Phẩm', icon: 'fa-solid fa-boxes-stacked' },
    { id: 'categories', label: 'Quản Lý Danh Mục', icon: 'fa-solid fa-folder-tree' },
    { id: 'users', label: 'Quản Lý Người Dùng & Roles', icon: 'fa-solid fa-users-gear' },
    { id: 'logs', label: 'Nhật Ký API Backend', icon: 'fa-solid fa-terminal' },
  ],
}) {
  return (
    <div className="admin-nav-tabs">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          className={`admin-nav-btn ${currentTab === tab.id ? 'active' : ''}`}
          onClick={() => onSelectTab(tab.id)}
        >
          <i className={tab.icon}></i>
          {tab.label}
        </button>
      ))}
    </div>
  )
}
