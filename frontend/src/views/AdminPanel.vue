<!--
Caduceus 管理面板页面
提供用户管理、角色管理和组管理的完整 CRUD 功能
支持 Tab 切换、表格展示、弹窗表单编辑、行内操作
-->
<template>
  <AppLayout>
    <div class="admin-panel">
      <div class="admin-header">
        <h1>管理面板</h1>
      </div>

      <!-- Tab 切换栏 -->
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="['tab-btn', { active: activeTab === tab.key }]"
          @click="switchTab(tab.key)"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- 用户管理 Tab -->
      <div v-if="activeTab === 'users'" class="tab-content">
        <div class="section-header">
          <h2>用户管理</h2>
          <button class="btn btn-primary" @click="openUserModal()">+ 新建用户</button>
        </div>

        <div v-if="usersLoading" class="loading-text">加载中...</div>
        <div v-else-if="users.length === 0" class="empty-text">暂无用户数据</div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>邮箱</th>
              <th>是否启用</th>
              <th>角色列表</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.username }}</td>
              <td>{{ user.email || '-' }}</td>
              <td>
                <span :class="['badge', user.is_active ? 'badge-success' : 'badge-danger']">
                  {{ user.is_active ? '启用' : '禁用' }}
                </span>
              </td>
              <td>{{ formatUserRoles(user) }}</td>
              <td class="actions-cell">
                <button class="btn btn-sm btn-outline" @click="openUserModal(user)">编辑</button>
                <button
                  :class="['btn', 'btn-sm', user.is_active ? 'btn-warning' : 'btn-success']"
                  @click="toggleUserActive(user)"
                >
                  {{ user.is_active ? '禁用' : '启用' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 角色管理 Tab -->
      <div v-if="activeTab === 'roles'" class="tab-content">
        <div class="section-header">
          <h2>角色管理</h2>
          <button class="btn btn-primary" @click="openRoleModal()">+ 新建角色</button>
        </div>

        <div v-if="rolesLoading" class="loading-text">加载中...</div>
        <div v-else-if="roles.length === 0" class="empty-text">暂无角色数据</div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>名称</th>
              <th>角色类型</th>
              <th>描述</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="role in roles" :key="role.id">
              <td>{{ role.id }}</td>
              <td>{{ role.name }}</td>
              <td>{{ role.role_type_display }}</td>
              <td>{{ role.description || '-' }}</td>
              <td class="actions-cell">
                <button class="btn btn-sm btn-outline" @click="openRoleModal(role)">编辑</button>
                <button class="btn btn-sm btn-danger" @click="deleteRole(role)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 组管理 Tab -->
      <div v-if="activeTab === 'groups'" class="tab-content">
        <div class="section-header">
          <h2>组管理</h2>
          <button class="btn btn-primary" @click="openGroupModal()">+ 新建组</button>
        </div>

        <div v-if="groupsLoading" class="loading-text">加载中...</div>
        <div v-else-if="groups.length === 0" class="empty-text">暂无组数据</div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>名称</th>
              <th>描述</th>
              <th>成员数</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="group in groups" :key="group.id">
              <td>{{ group.id }}</td>
              <td>{{ group.name }}</td>
              <td>{{ group.description || '-' }}</td>
              <td>{{ group.member_count ?? 0 }}</td>
              <td class="actions-cell">
                <button class="btn btn-sm btn-outline" @click="openGroupModal(group)">编辑</button>
                <button class="btn btn-sm btn-danger" @click="deleteGroup(group)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 用户弹窗 -->
      <div v-if="showUserModal" class="modal-overlay" @click.self="closeUserModal">
        <div class="modal">
          <h3>{{ editingUser ? '编辑用户' : '新建用户' }}</h3>
          <div class="form-group">
            <label>用户名 <span class="required">*</span></label>
            <input v-model="userForm.username" type="text" placeholder="请输入用户名" />
          </div>
          <div class="form-group">
            <label>密码 <span v-if="!editingUser" class="required">*</span></label>
            <input v-model="userForm.password" type="password" :placeholder="editingUser ? '留空则不修改' : '请输入密码'" />
          </div>
          <div v-if="!editingUser" class="form-group">
            <label>确认密码 <span class="required">*</span></label>
            <input v-model="userForm.password_confirm" type="password" placeholder="请再次输入密码" />
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input v-model="userForm.email" type="email" placeholder="请输入邮箱" />
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="userForm.is_active" type="checkbox" />
              启用账号
            </label>
          </div>
          <div class="form-group">
            <label>角色分配</label>
            <div class="checkbox-group">
              <label v-for="role in allRoles" :key="role.id" class="checkbox-label">
                <input
                  type="checkbox"
                  :value="role.id"
                  :checked="userForm.role_ids.includes(role.id)"
                  @change="toggleUserRole(role.id)"
                />
                {{ role.name }}
              </label>
            </div>
          </div>
          <div v-if="userFormError" class="form-error">{{ userFormError }}</div>
          <div class="modal-actions">
            <button class="btn btn-outline" @click="closeUserModal">取消</button>
            <button class="btn btn-primary" :disabled="userFormSaving" @click="saveUser">
              {{ userFormSaving ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 角色弹窗 -->
      <div v-if="showRoleModal" class="modal-overlay" @click.self="closeRoleModal">
        <div class="modal">
          <h3>{{ editingRole ? '编辑角色' : '新建角色' }}</h3>
          <div class="form-group">
            <label>名称 <span class="required">*</span></label>
            <input v-model="roleForm.name" type="text" placeholder="请输入角色名称" />
          </div>
          <div class="form-group">
            <label>角色类型 <span class="required">*</span></label>
            <select v-model="roleForm.role_type">
              <option value="initiator">发起人</option>
              <option value="executor">执行人</option>
              <option value="admin">管理员</option>
            </select>
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="roleForm.description" rows="3" placeholder="请输入角色描述"></textarea>
          </div>
          <div v-if="roleFormError" class="form-error">{{ roleFormError }}</div>
          <div class="modal-actions">
            <button class="btn btn-outline" @click="closeRoleModal">取消</button>
            <button class="btn btn-primary" :disabled="roleFormSaving" @click="saveRole">
              {{ roleFormSaving ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 组弹窗 -->
      <div v-if="showGroupModal" class="modal-overlay" @click.self="closeGroupModal">
        <div class="modal">
          <h3>{{ editingGroup ? '编辑组' : '新建组' }}</h3>
          <div class="form-group">
            <label>名称 <span class="required">*</span></label>
            <input v-model="groupForm.name" type="text" placeholder="请输入组名称" />
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="groupForm.description" rows="3" placeholder="请输入组描述"></textarea>
          </div>
          <div v-if="groupFormError" class="form-error">{{ groupFormError }}</div>
          <div class="modal-actions">
            <button class="btn btn-outline" @click="closeGroupModal">取消</button>
            <button class="btn btn-primary" :disabled="groupFormSaving" @click="saveGroup">
              {{ groupFormSaving ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 全局消息提示 -->
      <div v-if="toastMessage" :class="['toast', 'toast-' + toastType]" @click="toastMessage = ''">
        {{ toastMessage }}
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
/**
 * Caduceus AdminPanel 页面脚本
 * 管理用户/角色/组的 CRUD 操作，包含表格展示、弹窗表单和状态处理
 */
import { ref, reactive, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import client from '@/api/client'

// ---- 状态定义 ----

const activeTab = ref('users')
const tabs = [
  { key: 'users', label: '用户管理' },
  { key: 'roles', label: '角色管理' },
  { key: 'groups', label: '组管理' }
]

// 用户数据
const users = ref([])
const usersLoading = ref(false)

// 角色数据
const roles = ref([])
const rolesLoading = ref(false)
const allRoles = ref([])

// 组数据
const groups = ref([])
const groupsLoading = ref(false)

// Toast 消息
const toastMessage = ref('')
const toastType = ref('success')

// ---- 用户弹窗状态 ----
const showUserModal = ref(false)
const editingUser = ref(null)
const userFormSaving = ref(false)
const userFormError = ref('')
const userForm = reactive({
  username: '',
  password: '',
  password_confirm: '',
  email: '',
  is_active: true,
  role_ids: []
})

// ---- 角色弹窗状态 ----
const showRoleModal = ref(false)
const editingRole = ref(null)
const roleFormSaving = ref(false)
const roleFormError = ref('')
const roleForm = reactive({
  name: '',
  role_type: 'initiator',
  description: ''
})

// ---- 组弹窗状态 ----
const showGroupModal = ref(false)
const editingGroup = ref(null)
const groupFormSaving = ref(false)
const groupFormError = ref('')
const groupForm = reactive({
  name: '',
  description: ''
})

// ---- 通用工具函数 ----

/** 显示 toast 消息，2.5 秒后自动消失 */
function showToast(message, type = 'success') {
  toastMessage.value = message
  toastType.value = type
  setTimeout(() => { toastMessage.value = '' }, 2500)
}

/** 格式化用户关联的角色列表为逗号分隔字符串 */
function formatUserRoles(user) {
  if (!user.role_assignments || user.role_assignments.length === 0) return '-'
  return user.role_assignments.map((a) => a.role_name).join('、')
}

/** 切换 Tab 并加载对应数据 */
function switchTab(tabKey) {
  activeTab.value = tabKey
  if (tabKey === 'users' && users.value.length === 0) loadUsers()
  if (tabKey === 'roles' && roles.value.length === 0) loadRoles()
  if (tabKey === 'groups' && groups.value.length === 0) loadGroups()
}

// ---- 用户 CRUD ----

/** 加载用户列表 */
async function loadUsers() {
  usersLoading.value = true
  try {
    const res = await client.get('/accounts/users/')
    users.value = Array.isArray(res.data) ? res.data : (res.data?.results || [])
  } catch (e) {
    console.error('加载用户列表失败:', e)
    showToast('加载用户列表失败', 'error')
  } finally {
    usersLoading.value = false
  }
}

/** 打开用户弹窗（新建或编辑） */
async function openUserModal(user = null) {
  editingUser.value = user
  userFormError.value = ''
  if (user) {
    // 编辑模式：回填用户数据
    userForm.username = user.username
    userForm.password = ''
    userForm.password_confirm = ''
    userForm.email = user.email || ''
    userForm.is_active = user.is_active
    userForm.role_ids = (user.role_assignments || []).map((a) => a.role)
  } else {
    // 新建模式：重置表单
    userForm.username = ''
    userForm.password = ''
    userForm.password_confirm = ''
    userForm.email = ''
    userForm.is_active = true
    userForm.role_ids = []
  }
  // 确保角色列表已加载
  if (allRoles.value.length === 0) {
    try {
      const res = await client.get('/accounts/roles/')
      allRoles.value = Array.isArray(res.data) ? res.data : (res.data?.results || [])
    } catch (e) {
      console.error('加载角色列表失败:', e)
    }
  }
  showUserModal.value = true
}

/** 关闭用户弹窗 */
function closeUserModal() {
  showUserModal.value = false
  editingUser.value = null
}

/** 切换用户弹窗中的角色勾选 */
function toggleUserRole(roleId) {
  const idx = userForm.role_ids.indexOf(roleId)
  if (idx > -1) {
    userForm.role_ids.splice(idx, 1)
  } else {
    userForm.role_ids.push(roleId)
  }
}

/** 保存用户（新建或编辑） */
async function saveUser() {
  userFormError.value = ''
  // 前端验证
  if (!userForm.username) {
    userFormError.value = '请输入用户名'
    return
  }
  if (!editingUser.value && !userForm.password) {
    userFormError.value = '请输入密码'
    return
  }
  if (!editingUser.value && userForm.password !== userForm.password_confirm) {
    userFormError.value = '两次密码输入不一致'
    return
  }

  userFormSaving.value = true
  try {
    if (editingUser.value) {
      // 编辑用户：PATCH 更新基本信息 + is_active
      const patchData = {
        email: userForm.email,
        first_name: userForm.first_name || '',
        last_name: userForm.last_name || '',
        profile: userForm.profile || {}
      }
      // 同时更新 is_active
      await client.patch(`/accounts/users/${editingUser.value.id}/`, patchData)
      // 单独 PATCH is_active
      await client.patch(`/accounts/users/${editingUser.value.id}/`, {
        is_active: userForm.is_active
      }).catch(() => {})
      // 同步角色分配
      await syncUserRoles(editingUser.value)
      showToast('用户更新成功')
    } else {
      // 新建用户：POST 创建
      const createData = {
        username: userForm.username,
        email: userForm.email,
        password: userForm.password,
        password_confirm: userForm.password_confirm
      }
      // 如果 is_active 为 false，创建后再 PATCH 禁用
      const res = await client.post('/accounts/users/', createData)
      const newUserId = res.data.id
      if (!userForm.is_active) {
        await client.patch(`/accounts/users/${newUserId}/`, { is_active: false }).catch(() => {})
      }
      // 创建角色分配
      await createUserRoles(newUserId, userForm.role_ids)
      showToast('用户创建成功')
    }
    closeUserModal()
    await loadUsers()
  } catch (e) {
    const detail = e.response?.data
    if (detail) {
      // 提取 DRF 错误信息
      const messages = []
      for (const [key, val] of Object.entries(detail)) {
        const valStr = Array.isArray(val) ? val.join('；') : val
        messages.push(`${key}: ${valStr}`)
      }
      userFormError.value = messages.join('\n') || '保存失败'
    } else {
      userFormError.value = '保存失败，请重试'
    }
  } finally {
    userFormSaving.value = false
  }
}

/** 切换用户启用/禁用状态 */
async function toggleUserActive(user) {
  try {
    await client.patch(`/accounts/users/${user.id}/`, { is_active: !user.is_active })
    user.is_active = !user.is_active
    showToast(user.is_active ? '用户已启用' : '用户已禁用')
  } catch (e) {
    showToast('操作失败', 'error')
  }
}

/** 为用户创建角色分配 */
async function createUserRoles(userId, roleIds) {
  for (const roleId of roleIds) {
    try {
      await client.post('/accounts/role-assignments/', { user: userId, role: roleId })
    } catch (e) {
      console.error(`创建角色分配失败 (user=${userId}, role=${roleId}):`, e)
    }
  }
}

/** 同步用户的角色分配（对比新增和删除） */
async function syncUserRoles(user) {
  const currentRoleIds = (user.role_assignments || []).map((a) => a.role)
  const targetRoleIds = userForm.role_ids

  // 需要新增的角色
  const toAdd = targetRoleIds.filter((id) => !currentRoleIds.includes(id))
  // 需要删除的角色分配
  const toRemove = (user.role_assignments || []).filter((a) => !targetRoleIds.includes(a.role))

  for (const roleId of toAdd) {
    try {
      await client.post('/accounts/role-assignments/', { user: user.id, role: roleId })
    } catch (e) {
      console.error(`新增角色分配失败 (user=${user.id}, role=${roleId}):`, e)
    }
  }
  for (const assignment of toRemove) {
    try {
      await client.delete(`/accounts/role-assignments/${assignment.id}/`)
    } catch (e) {
      console.error(`删除角色分配失败 (id=${assignment.id}):`, e)
    }
  }
}

// ---- 角色 CRUD ----

/** 加载角色列表 */
async function loadRoles() {
  rolesLoading.value = true
  try {
    const res = await client.get('/accounts/roles/')
    roles.value = Array.isArray(res.data) ? res.data : (res.data?.results || [])
  } catch (e) {
    console.error('加载角色列表失败:', e)
    showToast('加载角色列表失败', 'error')
  } finally {
    rolesLoading.value = false
  }
}

/** 打开角色弹窗（新建或编辑） */
function openRoleModal(role = null) {
  editingRole.value = role
  roleFormError.value = ''
  if (role) {
    roleForm.name = role.name
    roleForm.role_type = role.role_type
    roleForm.description = role.description || ''
  } else {
    roleForm.name = ''
    roleForm.role_type = 'initiator'
    roleForm.description = ''
  }
  showRoleModal.value = true
}

/** 关闭角色弹窗 */
function closeRoleModal() {
  showRoleModal.value = false
  editingRole.value = null
}

/** 保存角色（新建或编辑） */
async function saveRole() {
  roleFormError.value = ''
  if (!roleForm.name) {
    roleFormError.value = '请输入角色名称'
    return
  }

  roleFormSaving.value = true
  try {
    const data = {
      name: roleForm.name,
      role_type: roleForm.role_type,
      description: roleForm.description
    }
    if (editingRole.value) {
      await client.patch(`/accounts/roles/${editingRole.value.id}/`, data)
      showToast('角色更新成功')
    } else {
      await client.post('/accounts/roles/', data)
      showToast('角色创建成功')
    }
    closeRoleModal()
    await loadRoles()
    // 刷新角色缓存供用户弹窗使用
    await refreshAllRoles()
  } catch (e) {
    const detail = e.response?.data
    if (detail) {
      const messages = []
      for (const [key, val] of Object.entries(detail)) {
        messages.push(`${key}: ${Array.isArray(val) ? val.join('；') : val}`)
      }
      roleFormError.value = messages.join('\n') || '保存失败'
    } else {
      roleFormError.value = '保存失败，请重试'
    }
  } finally {
    roleFormSaving.value = false
  }
}

/** 删除角色 */
async function deleteRole(role) {
  if (!confirm(`确定要删除角色「${role.name}」吗？此操作不可撤销。`)) return
  try {
    await client.delete(`/accounts/roles/${role.id}/`)
    showToast('角色已删除')
    await loadRoles()
    await refreshAllRoles()
  } catch (e) {
    showToast('删除失败', 'error')
  }
}

/** 刷新角色缓存 */
async function refreshAllRoles() {
  try {
    const res = await client.get('/accounts/roles/')
    allRoles.value = Array.isArray(res.data) ? res.data : (res.data?.results || [])
  } catch (e) {
    console.error('刷新角色缓存失败:', e)
  }
}

// ---- 组 CRUD ----

/** 加载组列表 */
async function loadGroups() {
  groupsLoading.value = true
  try {
    const res = await client.get('/accounts/groups/')
    groups.value = Array.isArray(res.data) ? res.data : (res.data?.results || [])
  } catch (e) {
    console.error('加载组列表失败:', e)
    showToast('加载组列表失败', 'error')
  } finally {
    groupsLoading.value = false
  }
}

/** 打开组弹窗（新建或编辑） */
function openGroupModal(group = null) {
  editingGroup.value = group
  groupFormError.value = ''
  if (group) {
    groupForm.name = group.name
    groupForm.description = group.description || ''
  } else {
    groupForm.name = ''
    groupForm.description = ''
  }
  showGroupModal.value = true
}

/** 关闭组弹窗 */
function closeGroupModal() {
  showGroupModal.value = false
  editingGroup.value = null
}

/** 保存组（新建或编辑） */
async function saveGroup() {
  groupFormError.value = ''
  if (!groupForm.name) {
    groupFormError.value = '请输入组名称'
    return
  }

  groupFormSaving.value = true
  try {
    const data = {
      name: groupForm.name,
      description: groupForm.description
    }
    if (editingGroup.value) {
      await client.patch(`/accounts/groups/${editingGroup.value.id}/`, data)
      showToast('组更新成功')
    } else {
      await client.post('/accounts/groups/', data)
      showToast('组创建成功')
    }
    closeGroupModal()
    await loadGroups()
  } catch (e) {
    const detail = e.response?.data
    if (detail) {
      const messages = []
      for (const [key, val] of Object.entries(detail)) {
        messages.push(`${key}: ${Array.isArray(val) ? val.join('；') : val}`)
      }
      groupFormError.value = messages.join('\n') || '保存失败'
    } else {
      groupFormError.value = '保存失败，请重试'
    }
  } finally {
    groupFormSaving.value = false
  }
}

/** 删除组 */
async function deleteGroup(group) {
  if (!confirm(`确定要删除组「${group.name}」吗？此操作不可撤销。`)) return
  try {
    await client.delete(`/accounts/groups/${group.id}/`)
    showToast('组已删除')
    await loadGroups()
  } catch (e) {
    showToast('删除失败', 'error')
  }
}

// ---- 初始化 ----

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.admin-panel {
  position: relative;
  padding: 24px;
}

.admin-header h1 {
  font-size: 24px;
  margin-bottom: 24px;
  margin-top: 0;
  color: #1a1a2e;
}

/* ---- Tab 切换栏 ---- */
.tabs {
  display: flex;
  gap: 0;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 24px;
}

.tab-btn {
  padding: 10px 24px;
  border: none;
  background: none;
  font-size: 15px;
  color: #666;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: color 0.2s, border-color 0.2s;
}

.tab-btn:hover {
  color: #667eea;
}

.tab-btn.active {
  color: #667eea;
  border-bottom-color: #667eea;
  font-weight: 600;
}

/* ---- 区域标题 ---- */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 18px;
  margin: 0;
  color: #333;
}

/* ---- 表格样式 ---- */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table thead th {
  background: #f5f5f5;
  color: #555;
  font-weight: 600;
  text-align: left;
  padding: 12px 16px;
  border-bottom: 2px solid #e0e0e0;
  white-space: nowrap;
}

.data-table tbody td {
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
}

.data-table tbody tr:nth-child(even) {
  background: #fafafa;
}

.data-table tbody tr:hover {
  background: #eef0ff;
}

.actions-cell {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* ---- Badge ---- */
.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge-success {
  background: #d1fae5;
  color: #065f46;
}

.badge-danger {
  background: #fee2e2;
  color: #991b1b;
}

/* ---- 按钮 ---- */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn:hover {
  opacity: 0.85;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm {
  padding: 5px 12px;
  font-size: 13px;
}

.btn-primary {
  background: #667eea;
  color: #fff;
}

.btn-outline {
  background: #fff;
  color: #555;
  border: 1px solid #ccc;
}

.btn-outline:hover {
  border-color: #667eea;
  color: #667eea;
}

.btn-danger {
  background: #ef4444;
  color: #fff;
}

.btn-warning {
  background: #f59e0b;
  color: #fff;
}

.btn-success {
  background: #10b981;
  color: #fff;
}

/* ---- 状态文本 ---- */
.loading-text {
  text-align: center;
  color: #999;
  padding: 48px 0;
}

.empty-text {
  text-align: center;
  color: #999;
  padding: 48px 0;
}

/* ---- 弹窗遮罩 ---- */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal {
  background: #fff;
  border-radius: 12px;
  padding: 28px 32px;
  width: 100%;
  max-width: 480px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.modal h3 {
  margin: 0 0 20px;
  font-size: 18px;
  color: #1a1a2e;
}

/* ---- 表单 ---- */
.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #444;
  margin-bottom: 6px;
}

.required {
  color: #ef4444;
}

.form-group input[type='text'],
.form-group input[type='email'],
.form-group input[type='password'],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

.checkbox-label {
  display: flex !important;
  align-items: center;
  gap: 8px;
  font-weight: 400 !important;
  cursor: pointer;
}

.checkbox-label input[type='checkbox'] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 20px;
  padding: 8px 0;
}

.form-error {
  color: #ef4444;
  font-size: 13px;
  margin-bottom: 12px;
  white-space: pre-line;
  padding: 8px 12px;
  background: #fef2f2;
  border-radius: 6px;
}

/* ---- 弹窗按钮 ---- */
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

/* ---- Toast ---- */
.toast {
  position: fixed;
  bottom: 32px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 28px;
  border-radius: 8px;
  font-size: 14px;
  color: #fff;
  cursor: pointer;
  z-index: 300;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  animation: toastFadeIn 0.3s ease;
}

.toast-success {
  background: #10b981;
}

.toast-error {
  background: #ef4444;
}

@keyframes toastFadeIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}
</style>
