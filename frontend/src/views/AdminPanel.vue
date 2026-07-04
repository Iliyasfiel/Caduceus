<!--
Caduceus 管理面板页面
提供用户管理、角色管理和组管理的完整 CRUD 功能
支持 Tab 切换、表格展示、弹窗表单编辑、行内操作
模板 / 样式 polish：使用 UiTabs / UiCard / UiBadge / UiButton / UiInput / UiSelect / UiModal。
业务逻辑（client API / CRUD / 校验 / 角色同步）零改动。
-->
<template>
  <AppLayout>
    <div class="admin-panel">
      <div class="admin-header">
        <h1 class="admin-header__title">管理面板</h1>
      </div>

      <!-- Tab 切换栏 -->
      <UiTabs
        v-model:activeKey="activeTab"
        :tabs="tabs"
      />

      <!-- 用户管理 Tab -->
      <div v-if="activeTab === 'users'" class="tab-content">
        <div class="section-header">
          <h2>用户管理</h2>
          <UiButton variant="primary" size="md" @click="openUserModal()">
            + 新建用户
          </UiButton>
        </div>

        <div v-if="usersLoading" class="loading-text">加载中...</div>
        <div v-else-if="users.length === 0" class="empty-text">暂无用户数据</div>
        <UiCard v-else class="table-card">
          <table class="data-table">
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
                  <UiBadge :tone="user.is_active ? 'success' : 'danger'">
                    {{ user.is_active ? '启用' : '禁用' }}
                  </UiBadge>
                </td>
                <td>{{ formatUserRoles(user) }}</td>
                <td class="actions-cell">
                  <button class="btn-action" @click="openUserModal(user)">编辑</button>
                  <button
                    class="btn-action"
                    :class="user.is_active ? 'btn-action--warning' : 'btn-action--success'"
                    @click="toggleUserActive(user)"
                  >
                    {{ user.is_active ? '禁用' : '启用' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </UiCard>
      </div>

      <!-- 角色管理 Tab -->
      <div v-if="activeTab === 'roles'" class="tab-content">
        <div class="section-header">
          <h2>角色管理</h2>
          <UiButton variant="primary" size="md" @click="openRoleModal()">
            + 新建角色
          </UiButton>
        </div>

        <div v-if="rolesLoading" class="loading-text">加载中...</div>
        <div v-else-if="roles.length === 0" class="empty-text">暂无角色数据</div>
        <UiCard v-else class="table-card">
          <table class="data-table">
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
                  <button class="btn-action" @click="openRoleModal(role)">编辑</button>
                  <button class="btn-action btn-action--danger" @click="deleteRole(role)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </UiCard>
      </div>

      <!-- 组管理 Tab -->
      <div v-if="activeTab === 'groups'" class="tab-content">
        <div class="section-header">
          <h2>组管理</h2>
          <UiButton variant="primary" size="md" @click="openGroupModal()">
            + 新建组
          </UiButton>
        </div>

        <div v-if="groupsLoading" class="loading-text">加载中...</div>
        <div v-else-if="groups.length === 0" class="empty-text">暂无组数据</div>
        <UiCard v-else class="table-card">
          <table class="data-table">
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
                  <button class="btn-action" @click="openGroupModal(group)">编辑</button>
                  <button class="btn-action btn-action--danger" @click="deleteGroup(group)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </UiCard>
      </div>

      <!-- 用户弹窗 -->
      <UiModal
        v-model="showUserModal"
        :title="editingUser ? '编辑用户' : '新建用户'"
        size="md"
      >
        <div class="form-stack">
          <div class="form-group">
            <label>用户名 <span class="required">*</span></label>
            <UiInput v-model="userForm.username" placeholder="请输入用户名" />
          </div>
          <div class="form-group">
            <label>密码 <span v-if="!editingUser" class="required">*</span></label>
            <UiInput v-model="userForm.password" type="password" :placeholder="editingUser ? '留空则不修改' : '请输入密码'" />
          </div>
          <div v-if="!editingUser" class="form-group">
            <label>确认密码 <span class="required">*</span></label>
            <UiInput v-model="userForm.password_confirm" type="password" placeholder="请再次输入密码" />
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <UiInput v-model="userForm.email" type="email" placeholder="请输入邮箱" />
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
          <p v-if="userFormError" class="form-error">{{ userFormError }}</p>
        </div>
        <template #footer>
          <UiButton variant="secondary" @click="closeUserModal">取消</UiButton>
          <UiButton
            variant="primary"
            :loading="userFormSaving"
            @click="saveUser"
          >
            保存
          </UiButton>
        </template>
      </UiModal>

      <!-- 角色弹窗 -->
      <UiModal
        v-model="showRoleModal"
        :title="editingRole ? '编辑角色' : '新建角色'"
        size="md"
      >
        <div class="form-stack">
          <div class="form-group">
            <label>名称 <span class="required">*</span></label>
            <UiInput v-model="roleForm.name" placeholder="请输入角色名称" />
          </div>
          <div class="form-group">
            <label>角色类型 <span class="required">*</span></label>
            <select v-model="roleForm.role_type" class="form-input">
              <option value="initiator">发起人</option>
              <option value="executor">执行人</option>
              <option value="admin">管理员</option>
            </select>
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="roleForm.description" rows="3" class="form-input" placeholder="请输入角色描述"></textarea>
          </div>
          <p v-if="roleFormError" class="form-error">{{ roleFormError }}</p>
        </div>
        <template #footer>
          <UiButton variant="secondary" @click="closeRoleModal">取消</UiButton>
          <UiButton
            variant="primary"
            :loading="roleFormSaving"
            @click="saveRole"
          >
            保存
          </UiButton>
        </template>
      </UiModal>

      <!-- 组弹窗 -->
      <UiModal
        v-model="showGroupModal"
        :title="editingGroup ? '编辑组' : '新建组'"
        size="md"
      >
        <div class="form-stack">
          <div class="form-group">
            <label>名称 <span class="required">*</span></label>
            <UiInput v-model="groupForm.name" placeholder="请输入组名称" />
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="groupForm.description" rows="3" class="form-input" placeholder="请输入组描述"></textarea>
          </div>
          <p v-if="groupFormError" class="form-error">{{ groupFormError }}</p>
        </div>
        <template #footer>
          <UiButton variant="secondary" @click="closeGroupModal">取消</UiButton>
          <UiButton
            variant="primary"
            :loading="groupFormSaving"
            @click="saveGroup"
          >
            保存
          </UiButton>
        </template>
      </UiModal>
    </div>
  </AppLayout>
</template>

<script setup>
/**
 * Caduceus AdminPanel 页面脚本
 * 业务逻辑零改动：所有 client.get/patch/post/delete 调用、表单校验、角色同步逻辑保留。
 * 仅 showToast() 替换为 useToast() 调用（行为等价）。
 */
import { ref, reactive, onMounted, watch } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import client from '@/api/client'
import { useToast } from '@/stores/toast'
import { useConfirm } from '@/stores/confirm'
import {
  UiButton, UiInput, UiCard, UiBadge, UiModal, UiTabs
} from '@/components/ui'

const toast = useToast()
const confirm = useConfirm()

// ---- 状态定义 ----

const activeTab = ref('users')
const tabs = [
  { key: 'users',  label: '用户管理' },
  { key: 'roles',  label: '角色管理' },
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

// 监听 tab 切换
watch(activeTab, switchTab)

// ---- 用户 CRUD ----

/** 加载用户列表 */
async function loadUsers() {
  usersLoading.value = true
  try {
    const res = await client.get('/accounts/users/')
    users.value = Array.isArray(res.data) ? res.data : (res.data?.results || [])
  } catch (e) {
    console.error('加载用户列表失败:', e)
    toast.error('加载用户列表失败')
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
      toast.success('用户更新成功')
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
      toast.success('用户创建成功')
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
    toast.success(user.is_active ? '用户已启用' : '用户已禁用')
  } catch (e) {
    toast.error('操作失败')
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
    toast.error('加载角色列表失败')
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
      toast.success('角色更新成功')
    } else {
      await client.post('/accounts/roles/', data)
      toast.success('角色创建成功')
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
  const ok = await confirm({
    title: '删除角色',
    message: `确定要删除角色「${role.name}」吗？此操作不可撤销。`,
    tone: 'danger',
    confirmText: '删除'
  })
  if (!ok) return
  try {
    await client.delete(`/accounts/roles/${role.id}/`)
    toast.success('角色已删除')
    await loadRoles()
    await refreshAllRoles()
  } catch (e) {
    toast.error('删除失败')
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
    toast.error('加载组列表失败')
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
      toast.success('组更新成功')
    } else {
      await client.post('/accounts/groups/', data)
      toast.success('组创建成功')
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
  const ok = await confirm({
    title: '删除组',
    message: `确定要删除组「${group.name}」吗？此操作不可撤销。`,
    tone: 'danger',
    confirmText: '删除'
  })
  if (!ok) return
  try {
    await client.delete(`/accounts/groups/${group.id}/`)
    toast.success('组已删除')
    await loadGroups()
  } catch (e) {
    toast.error('删除失败')
  }
}

// ---- 初始化 ----

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.admin-panel {
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.admin-header__title {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* ---- 区域标题 ---- */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.section-header h2 {
  font-size: var(--text-base);
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

/* ---- 表格 ---- */
.table-card :deep(.ui-card__body) {
  padding: 0;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.data-table thead th {
  background-color: var(--bg-canvas);
  color: var(--text-secondary);
  font-weight: 600;
  text-align: left;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  white-space: nowrap;
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table tbody td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-primary);
}

.data-table tbody tr:last-child td {
  border-bottom: 0;
}

.data-table tbody tr:hover {
  background-color: var(--bg-canvas);
}

.actions-cell {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.btn-action {
  padding: 4px 12px;
  border: 1px solid var(--color-input);
  background-color: var(--bg-surface);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--text-xs);
  transition: border-color var(--transition-fast), color var(--transition-fast);
}

.btn-action:hover {
  border-color: var(--text-primary);
  color: var(--text-primary);
}

.btn-action--danger {
  color: var(--color-destructive);
  border-color: var(--color-destructive);
}

.btn-action--danger:hover {
  background-color: var(--badge-danger-bg);
  color: var(--color-destructive);
  border-color: var(--color-destructive);
}

.btn-action--warning {
  color: var(--badge-warning-fg);
  border-color: var(--badge-warning-bg);
}

.btn-action--warning:hover {
  background-color: var(--badge-warning-bg);
  color: var(--badge-warning-fg);
  border-color: var(--badge-warning-fg);
}

.btn-action--success {
  color: var(--badge-success-fg);
  border-color: var(--badge-success-bg);
}

.btn-action--success:hover {
  background-color: var(--badge-success-bg);
  color: var(--badge-success-fg);
  border-color: var(--badge-success-fg);
}

/* ---- 状态文本 ---- */
.loading-text,
.empty-text {
  text-align: center;
  color: var(--text-muted);
  padding: var(--space-12) 0;
  font-size: var(--text-sm);
}

/* ---- 表单 ---- */
.form-stack {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-group label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.required {
  color: var(--color-destructive);
}

.form-input {
  width: 100%;
  padding: var(--space-3);
  border: 1px solid var(--color-input);
  border-radius: var(--radius-md);
  background-color: var(--bg-surface);
  font-size: var(--text-sm);
  color: var(--text-primary);
  outline: none;
  box-sizing: border-box;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  font-family: inherit;
}

.form-input:focus {
  border-color: var(--color-ring);
  box-shadow: 0 0 0 3px rgba(13, 13, 13, 0.08);
}

textarea.form-input {
  resize: vertical;
}

.checkbox-label {
  display: inline-flex !important;
  align-items: center;
  gap: var(--space-2);
  font-weight: 400 !important;
  cursor: pointer;
}

.checkbox-label input[type='checkbox'] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--text-primary);
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-5);
  padding: var(--space-2) 0;
}

.form-error {
  color: var(--color-destructive);
  font-size: var(--text-xs);
  white-space: pre-line;
  padding: var(--space-2) var(--space-3);
  background-color: var(--badge-danger-bg);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--color-destructive);
  margin: 0;
}
</style>