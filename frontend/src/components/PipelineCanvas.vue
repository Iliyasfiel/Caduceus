<!--
管线编辑器画布组件
基于 Vue Flow 的可拖拽管线编辑器
支持任务节点的添加、连接、编辑和删除
通过 v-model 输出 { nodes: [], edges: [] } 数据
-->
<template>
  <div class="pipeline-canvas" @keydown="onKeyDown" tabindex="0">
    <!-- 左侧面板：节点操作区 -->
    <aside class="left-panel">
      <div class="panel-header">
        <h3>任务节点</h3>
      </div>
      <button class="add-node-btn" @click="addNode">
        + 添加任务节点
      </button>

      <!-- 已添加节点列表摘要 -->
      <div class="node-list">
        <div
          v-for="node in nodes"
          :key="node.id"
          class="node-list-item"
          :class="{ active: selectedNodeId === node.id }"
          @click="selectNode(node.id)"
        >
          <span class="node-list-label">{{ node.data.label }}</span>
          <button class="node-list-delete" @click.stop="deleteNodeById(node.id)">×</button>
        </div>
        <div v-if="nodes.length === 0" class="node-list-empty">
          暂无节点，点击上方按钮添加
        </div>
      </div>
    </aside>

    <!-- 中间画布区 -->
    <div class="canvas-container" @click="deselectAll">
      <VueFlow
        v-model:nodes="nodes"
        v-model:edges="edges"
        :default-viewport="{ zoom: 1 }"
        :min-zoom="0.2"
        :max-zoom="4"
        @node-click="onNodeClick"
        @node-contextmenu="onNodeContextMenu"
        @pane-click="onPaneClick"
        @pane-contextmenu="onPaneContextMenu"
        @connect="onConnect"
        @edge-click="onEdgeClick"
        @edge-contextmenu="onEdgeContextMenu"
      >
        <template #node-default="nodeProps">
          <div class="custom-node" :class="{ selected: selectedNodeId === nodeProps.id }">
            <div class="custom-node-header">
              {{ nodeProps.data.label }}
            </div>
          </div>
        </template>
        <Controls position="bottom-right" />
      </VueFlow>

      <!-- 右键菜单 -->
      <div
        v-if="contextMenu.visible"
        class="context-menu"
        :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      >
        <div class="context-menu-item" @click="deleteContextTarget">
          删除
        </div>
      </div>
    </div>

    <!-- 右侧编辑面板：选中节点后显示 -->
    <aside class="right-panel" v-if="selectedNode">
      <div class="panel-header">
        <h3>节点编辑</h3>
        <button class="panel-close" @click="deselectAll">×</button>
      </div>

      <div class="edit-form">
        <!-- 节点名称 -->
        <div class="form-group">
          <label>节点名称</label>
          <input
            type="text"
            v-model="selectedNode.data.label"
            class="form-input"
            placeholder="输入节点名称"
          />
        </div>

        <!-- 字段配置 fields_config -->
        <div class="form-section">
          <div class="section-header">
            <label>字段配置</label>
            <button class="btn-small" @click="addField">+ 添加字段</button>
          </div>
          <div
            v-for="(field, idx) in selectedNode.data.fields_config"
            :key="idx"
            class="config-item"
          >
            <div class="config-item-header">
              <span>字段 {{ idx + 1 }}</span>
              <button class="btn-small btn-danger" @click="removeField(idx)">删除</button>
            </div>
            <div class="form-row">
              <label>Label</label>
              <input type="text" v-model="field.label" class="form-input" placeholder="字段标签" />
            </div>
            <div class="form-row">
              <label>类型</label>
              <select v-model="field.type" class="form-select">
                <option value="">请选择类型</option>
                <option v-for="opt in fieldTypeOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>
            <div class="form-row">
              <label>优先级角色</label>
              <div class="checkbox-group">
                <label
                  v-for="role in availableRoles"
                  :key="role.id"
                  class="checkbox-label"
                >
                  <input
                    type="checkbox"
                    :value="role.id"
                    v-model="field.priority_roles"
                  />
                  {{ role.label || role.name || role.id }}
                </label>
                <span v-if="availableRoles.length === 0" class="hint-text">无可用角色</span>
              </div>
            </div>
            <div class="form-row">
              <label class="switch-label">
                <span>公开字段</span>
                <input type="checkbox" v-model="field.is_public" class="switch-input" />
              </label>
            </div>
          </div>
          <div v-if="!selectedNode.data.fields_config || selectedNode.data.fields_config.length === 0" class="hint-text">
            暂无字段，点击上方按钮添加
          </div>
        </div>

        <!-- 角色配置 roles -->
        <div class="form-section">
          <div class="section-header">
            <label>角色配置</label>
            <button class="btn-small" @click="addRole">+ 添加角色</button>
          </div>
          <div
            v-for="(role, idx) in selectedNode.data.roles"
            :key="idx"
            class="config-item"
          >
            <div class="config-item-header">
              <span>角色 {{ idx + 1 }}</span>
              <button class="btn-small btn-danger" @click="removeRole(idx)">删除</button>
            </div>
            <div class="form-row">
              <label>角色</label>
              <select v-model="role.role_id" class="form-select">
                <option value="">请选择角色</option>
                <option
                  v-for="r in availableRoles"
                  :key="r.id"
                  :value="r.id"
                  :disabled="isRoleAssigned(r.id, idx)"
                >
                  {{ r.label || r.name || r.id }}
                </option>
              </select>
            </div>
            <div class="form-row">
              <label class="switch-label">
                <span>合并默认值</span>
                <input type="checkbox" v-model="role.merge_default" class="switch-input" />
              </label>
            </div>
            <div class="form-row">
              <label>合并时间窗口（秒）</label>
              <input
                type="number"
                v-model.number="role.merge_time_window"
                class="form-input"
                placeholder="秒"
                min="0"
              />
            </div>
          </div>
          <div v-if="!selectedNode.data.roles || selectedNode.data.roles.length === 0" class="hint-text">
            暂无角色，点击上方按钮添加
          </div>
        </div>

        <!-- 资源类型 resource_types -->
        <div class="form-section">
          <label>资源类型</label>
          <div class="tag-group">
            <span
              v-for="rt in availableResourceTypes"
              :key="rt.id"
              class="tag"
              :class="{ 'tag-active': isResourceSelected(rt.id) }"
              @click="toggleResourceType(rt.id)"
            >
              {{ rt.label || rt.name || rt.id }}
            </span>
            <span v-if="availableResourceTypes.length === 0" class="hint-text">无可用资源类型</span>
          </div>
        </div>

        <!-- 删除节点按钮 -->
        <div class="form-section">
          <button class="btn-danger-full" @click="deleteNodeById(selectedNode.id)">
            删除此节点
          </button>
        </div>
      </div>
    </aside>

    <!-- 右侧面板占位：未选中节点时的提示 -->
    <aside class="right-panel right-panel-empty" v-else>
      <div class="panel-placeholder">
        <p>点击画布中的节点以编辑</p>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Controls } from '@vue-flow/controls'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'

// ===================== Props & v-model =====================

// 通过 v-model 双向绑定管线数据 { nodes: [], edges: [] }
const model = defineModel({
  type: Object,
  default: () => ({ nodes: [], edges: [] })
})

// 可选的角色列表（由父组件传入）
const props = defineProps({
  availableRoles: {
    type: Array,
    default: () => []
  },
  availableResourceTypes: {
    type: Array,
    default: () => []
  }
})

// ===================== 本地状态 =====================

// 画布节点和边（与 VueFlow 双向绑定）
const nodes = ref([])
const edges = ref([])

// 当前选中的节点 / 边 ID
const selectedNodeId = ref(null)
const selectedEdgeId = ref(null)

// 右键菜单状态
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  type: null, // 'node' | 'edge'
  nodeId: null,
  edgeId: null
})

// 字段类型下拉选项
const fieldTypeOptions = [
  { value: 'text', label: '文本' },
  { value: 'number', label: '数字' },
  { value: 'select', label: '下拉选择' },
  { value: 'date', label: '日期' },
  { value: 'boolean', label: '布尔值' },
  { value: 'textarea', label: '多行文本' }
]

// ===================== 计算属性 =====================

// 当前选中的节点对象
const selectedNode = computed(() => {
  return nodes.value.find(n => n.id === selectedNodeId.value) || null
})

// ===================== 初始化数据同步 =====================

// 从 model 初始化 nodes / edges，兼容后端扁平格式和 Vue Flow 嵌套格式
function initFromModel() {
  if (model.value) {
    nodes.value = (model.value.nodes || []).map(n => ({
      id: n.id,
      type: n.type || 'default',
      position: n.position || { x: 250 + Math.random() * 200, y: 100 + Math.random() * 300 },
      data: {
        label: n.data?.label || n.label || '新节点',
        fields_config: n.data?.fields_config || n.fields_config || [],
        roles: n.data?.roles || n.roles || [],
        resource_types: n.data?.resource_types || n.resource_types || []
      }
    }))
    edges.value = (model.value.edges || []).map(e => ({ ...e }))
  }
}

initFromModel()

// 监听本地数据变化，同步回 model（转换为后端扁平格式）
watch(
  [nodes, edges],
  () => {
    model.value = {
      nodes: nodes.value.map(n => ({
        id: n.id,
        label: n.data?.label || '新节点',
        fields_config: n.data?.fields_config || [],
        roles: n.data?.roles || [],
        resource_types: n.data?.resource_types || []
      })),
      edges: JSON.parse(JSON.stringify(edges.value))
    }
  },
  { deep: true }
)

// 监听外部 model 变化，同步到本地（父组件加载已有管线时触发）
watch(
  () => model.value,
  (newVal) => {
    if (newVal && newVal.nodes && newVal.edges) {
      const externalIds = new Set(newVal.nodes.map(n => n.id))
      const localIds = new Set(nodes.value.map(n => n.id))
      if (externalIds.size !== localIds.size || ![...externalIds].every(id => localIds.has(id))) {
        // 转换为 Vue Flow 格式，兼容后端扁平格式
        nodes.value = newVal.nodes.map(n => ({
          id: n.id,
          type: n.type || 'default',
          position: n.position || { x: 250 + Math.random() * 200, y: 100 + Math.random() * 300 },
          data: {
            label: n.data?.label || n.label || '新节点',
            fields_config: n.data?.fields_config || n.fields_config || [],
            roles: n.data?.roles || n.roles || [],
            resource_types: n.data?.resource_types || n.resource_types || []
          }
        }))
        edges.value = newVal.edges.map(e => ({ ...e }))
      }
    }
  },
  { deep: true }
)

// ===================== 节点操作 =====================

// 添加新任务节点到画布
function addNode() {
  const newNode = {
    id: 'node_' + Date.now(),
    type: 'default',
    position: { x: 250 + Math.random() * 200, y: 100 + Math.random() * 300 },
    data: {
      label: '新节点',
      fields_config: [],
      roles: [],
      resource_types: []
    }
  }
  nodes.value.push(newNode)
  selectedNodeId.value = newNode.id
  selectedEdgeId.value = null
}

// 选中指定节点
function selectNode(nodeId) {
  selectedNodeId.value = nodeId
  selectedEdgeId.value = null
}

// 取消所有选中
function deselectAll() {
  selectedNodeId.value = null
  selectedEdgeId.value = null
  hideContextMenu()
}

// 通过 ID 删除节点及其关联边
function deleteNodeById(nodeId) {
  nodes.value = nodes.value.filter(n => n.id !== nodeId)
  edges.value = edges.value.filter(e => e.source !== nodeId && e.target !== nodeId)
  if (selectedNodeId.value === nodeId) {
    selectedNodeId.value = null
  }
}

// 通过 ID 删除边
function deleteEdgeById(edgeId) {
  edges.value = edges.value.filter(e => e.id !== edgeId)
  if (selectedEdgeId.value === edgeId) {
    selectedEdgeId.value = null
  }
}

// ===================== Vue Flow 事件处理 =====================

// 点击画布节点
function onNodeClick({ node }) {
  selectedNodeId.value = node.id
  selectedEdgeId.value = null
}

// 点击画布空白区域
function onPaneClick() {
  deselectAll()
}

// 点击画布连线
function onEdgeClick({ edge }) {
  selectedEdgeId.value = edge.id
  selectedNodeId.value = null
}

// 拖拽连线完成时创建新边
function onConnect(connection) {
  const newEdge = {
    id: 'edge_' + Date.now(),
    source: connection.source,
    target: connection.target,
    sourceHandle: connection.sourceHandle,
    targetHandle: connection.targetHandle
  }
  edges.value.push(newEdge)
}

// ===================== 右键菜单 =====================

// 节点右键菜单
function onNodeContextMenu(event) {
  event.preventDefault()
  contextMenu.value = {
    visible: true,
    x: event.x || event.clientX,
    y: event.y || event.clientY,
    type: 'node',
    nodeId: event.node.id,
    edgeId: null
  }
}

// 连线右键菜单
function onEdgeContextMenu(event) {
  event.preventDefault()
  contextMenu.value = {
    visible: true,
    x: event.x || event.clientX,
    y: event.y || event.clientY,
    type: 'edge',
    nodeId: null,
    edgeId: event.edge.id
  }
}

// 画布空白区域右键 - 仅隐藏菜单
function onPaneContextMenu(event) {
  event.preventDefault()
  hideContextMenu()
}

// 隐藏右键菜单
function hideContextMenu() {
  contextMenu.value = {
    visible: false,
    x: 0,
    y: 0,
    type: null,
    nodeId: null,
    edgeId: null
  }
}

// 执行右键菜单删除操作
function deleteContextTarget() {
  if (contextMenu.value.type === 'node' && contextMenu.value.nodeId) {
    deleteNodeById(contextMenu.value.nodeId)
  } else if (contextMenu.value.type === 'edge' && contextMenu.value.edgeId) {
    deleteEdgeById(contextMenu.value.edgeId)
  }
  hideContextMenu()
}

// ===================== 键盘事件 =====================

// Delete / Backspace 键删除选中元素
function onKeyDown(e) {
  // 避免在输入框中误触发删除
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
    return
  }
  if (e.key === 'Delete' || e.key === 'Backspace') {
    if (selectedNodeId.value) {
      deleteNodeById(selectedNodeId.value)
    } else if (selectedEdgeId.value) {
      deleteEdgeById(selectedEdgeId.value)
    }
  }
  if (e.key === 'Escape') {
    hideContextMenu()
  }
}

// ===================== 右侧编辑面板辅助方法 =====================

// 添加字段配置项（key 自动生成，用户只需填 label）
function addField() {
  if (!selectedNode.value) return
  if (!selectedNode.value.data.fields_config) {
    selectedNode.value.data.fields_config = []
  }
  // 自动生成 key：取当前已有字段中 field_N 的最大序号 + 1
  const fields = selectedNode.value.data.fields_config
  let maxIdx = -1
  fields.forEach(f => {
    const m = (f.key || '').match(/^field_(\d+)$/)
    if (m) maxIdx = Math.max(maxIdx, parseInt(m[1], 10))
  })
  const nextKey = `field_${Math.max(maxIdx + 1, fields.length)}`
  fields.push({
    key: nextKey,
    label: '',
    type: '',
    priority_roles: [],
    is_public: false
  })
}

// 删除字段配置项
function removeField(idx) {
  if (!selectedNode.value) return
  selectedNode.value.data.fields_config.splice(idx, 1)
}

// 添加角色配置项
function addRole() {
  if (!selectedNode.value) return
  if (!selectedNode.value.data.roles) {
    selectedNode.value.data.roles = []
  }
  selectedNode.value.data.roles.push({
    role_id: '',
    merge_default: false,
    merge_time_window: 0
  })
}

// 删除角色配置项
function removeRole(idx) {
  if (!selectedNode.value) return
  selectedNode.value.data.roles.splice(idx, 1)
}

// 判断角色是否已被当前节点其他配置项选中（避免重复选择）
function isRoleAssigned(roleId, currentIdx) {
  if (!selectedNode.value) return false
  return selectedNode.value.data.roles.some(
    (r, idx) => idx !== currentIdx && r.role_id === roleId
  )
}

// 判断资源类型是否已选中
function isResourceSelected(rtId) {
  if (!selectedNode.value) return false
  return (selectedNode.value.data.resource_types || []).includes(rtId)
}

// 切换资源类型选中状态
function toggleResourceType(rtId) {
  if (!selectedNode.value) return
  if (!selectedNode.value.data.resource_types) {
    selectedNode.value.data.resource_types = []
  }
  const idx = selectedNode.value.data.resource_types.indexOf(rtId)
  if (idx === -1) {
    selectedNode.value.data.resource_types.push(rtId)
  } else {
    selectedNode.value.data.resource_types.splice(idx, 1)
  }
}

// ===================== 生命周期 =====================

onMounted(() => {
  document.addEventListener('click', hideContextMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', hideContextMenu)
})
</script>

<style scoped>
.pipeline-canvas {
  display: flex;
  height: 100vh;
  width: 100%;
  background: #f9fafb;
  outline: none;
}

/* ==================== 左侧面板 ==================== */

.left-panel {
  width: 240px;
  min-width: 240px;
  background: #fff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.panel-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.add-node-btn {
  margin: 12px 16px;
  padding: 10px 16px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.add-node-btn:hover {
  background: #5a6fd6;
}

.node-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px 16px;
}

.node-list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  margin-bottom: 4px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
  background: #f3f4f6;
}

.node-list-item:hover {
  background: #e5e7eb;
}

.node-list-item.active {
  background: #ede9fe;
  border: 1px solid #a78bfa;
}

.node-list-label {
  font-size: 13px;
  color: #374151;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.node-list-delete {
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 18px;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}

.node-list-delete:hover {
  color: #ef4444;
}

.node-list-empty {
  text-align: center;
  color: #9ca3af;
  font-size: 13px;
  padding: 24px 0;
}

/* ==================== 画布区 ==================== */

.canvas-container {
  flex: 1;
  position: relative;
  min-width: 0;
}

/* 自定义节点样式 */
.custom-node {
  background: #fff;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  padding: 10px 16px;
  min-width: 120px;
  font-size: 14px;
  color: #1f2937;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.custom-node.selected {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
}

.custom-node-header {
  font-weight: 500;
  text-align: center;
}

/* 右键菜单 */
.context-menu {
  position: fixed;
  z-index: 1000;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  min-width: 120px;
  overflow: hidden;
}

.context-menu-item {
  padding: 8px 16px;
  font-size: 13px;
  color: #374151;
  cursor: pointer;
  transition: background 0.15s;
}

.context-menu-item:hover {
  background: #f3f4f6;
  color: #ef4444;
}

/* ==================== 右侧编辑面板 ==================== */

.right-panel {
  width: 340px;
  min-width: 340px;
  background: #fff;
  border-left: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.right-panel-empty {
  display: flex;
  align-items: center;
  justify-content: center;
}

.panel-placeholder {
  color: #9ca3af;
  font-size: 14px;
  text-align: center;
  padding: 24px;
}

.panel-close {
  background: none;
  border: none;
  font-size: 20px;
  color: #9ca3af;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}

.panel-close:hover {
  color: #374151;
}

.edit-form {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
}

.form-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  color: #1f2937;
  outline: none;
  transition: border-color 0.15s;
}

.form-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.15);
}

.form-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  color: #1f2937;
  background: #fff;
  outline: none;
  cursor: pointer;
}

.form-select:focus {
  border-color: #667eea;
}

/* 表单区块 */
.form-section {
  border-top: 1px solid #e5e7eb;
  padding-top: 12px;
}

.form-section > label {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
  display: block;
  margin-bottom: 8px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.section-header label {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
}

/* 配置项卡片 */
.config-item {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 8px;
}

.config-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-row label {
  font-size: 12px;
  color: #6b7280;
}

/* 按钮 */
.btn-small {
  padding: 4px 10px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-small:hover {
  background: #5a6fd6;
}

.btn-danger {
  background: #ef4444;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-danger-full {
  width: 100%;
  padding: 10px 16px;
  background: #ef4444;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-danger-full:hover {
  background: #dc2626;
}

/* Checkbox 组 */
.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #374151;
  cursor: pointer;
}

/* Switch 开关 */
.switch-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
}

.switch-input {
  width: 36px;
  height: 20px;
  cursor: pointer;
  accent-color: #667eea;
}

/* 标签组（资源类型多选） */
.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  padding: 4px 10px;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  font-size: 12px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.15s;
}

.tag:hover {
  background: #e5e7eb;
}

.tag-active {
  background: #ede9fe;
  border-color: #a78bfa;
  color: #7c3aed;
}

/* 提示文字 */
.hint-text {
  font-size: 12px;
  color: #9ca3af;
  text-align: center;
  padding: 8px 0;
}
</style>
