import { useEffect, useState } from 'react'
import Button from '../../../components/common/Button'
import Loading from '../../../components/common/Loading'
import RoleSelector from '../components/RoleSelector'
import UserForm from '../components/UserForm'
import UserList from '../components/UserList'
import { userService } from '../services/userService'

export default function UsersPage({ currentUser, showToast }) {
  const [users, setUsers] = useState([])
  const [roles, setRoles] = useState([])
  const [loading, setLoading] = useState(false)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [createLoading, setCreateLoading] = useState(false)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [usersData, rolesData] = await Promise.all([
        userService.list(),
        userService.listRoles(),
      ])
      setUsers(usersData || [])
      setRoles(rolesData || [])
    } catch (err) {
      showToast(err.message || 'Không thể tải danh sách người dùng', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleToggleStatus = async (user) => {
    if (user.id === currentUser?.id) {
      showToast('Bạn không thể tự khóa tài khoản của chính mình!', 'error')
      return
    }

    const nextStatus = !user.is_active
    const confirmMsg = nextStatus
      ? `Mở khóa cho tài khoản "${user.email}"?`
      : `Khóa tài khoản "${user.email}"? Người dùng này sẽ không thể đăng nhập.`

    if (!window.confirm(confirmMsg)) return

    try {
      await userService.toggleStatus(user.id, nextStatus)
      showToast(`Đã ${nextStatus ? 'mở khóa' : 'khóa'} tài khoản thành công!`, 'success')
      fetchData()
    } catch (err) {
      showToast(err.message || 'Cập nhật trạng thái thất bại', 'error')
    }
  }

  const handleChangeRole = async (userId, roleId) => {
    try {
      await userService.changeRole(userId, roleId)
      showToast('Cập nhật vai trò thành công!', 'success')
      fetchData()
    } catch (err) {
      showToast(err.message || 'Lỗi cập nhật vai trò', 'error')
    }
  }

  const handleCreateUser = async (data) => {
    setCreateLoading(true)
    try {
      await userService.create(data)
      showToast(`Đã tạo tài khoản "${data.email}" thành công!`, 'success')
      setIsCreateOpen(false)
      fetchData()
    } catch (err) {
      showToast(err.message || 'Lỗi khi tạo người dùng mới', 'error')
    } finally {
      setCreateLoading(false)
    }
  }

  const handleRoleCreated = async (roleData) => {
    await userService.createRole(roleData)
    await fetchData()
  }

  return (
    <div className="card">
      <div className="card-title">
        <span>
          <i className="fa-solid fa-users-gear" style={{ marginRight: 8, color: 'var(--accent-purple)' }}></i>
          Quản Lý Người Dùng & Phân Quyền ({users.length} tài khoản)
        </span>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <Button size="sm" variant="outline" icon="fa-solid fa-arrows-rotate" onClick={fetchData}>
            Làm mới
          </Button>
          <Button size="sm" variant="primary" icon="fa-solid fa-user-plus" onClick={() => setIsCreateOpen(true)}>
            Thêm Người Dùng
          </Button>
        </div>
      </div>

      {/* Tổng quan Roles */}
      <RoleSelector
        roles={roles}
        users={users}
        onRoleCreated={handleRoleCreated}
        showToast={showToast}
      />

      {loading ? (
        <Loading text="Đang tải danh sách người dùng..." />
      ) : (
        <UserList
          users={users}
          roles={roles}
          currentUser={currentUser}
          onToggleStatus={handleToggleStatus}
          onChangeRole={handleChangeRole}
        />
      )}

      {/* Modal tạo user */}
      <UserForm
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onSubmit={handleCreateUser}
        roles={roles}
        loading={createLoading}
      />
    </div>
  )
}
