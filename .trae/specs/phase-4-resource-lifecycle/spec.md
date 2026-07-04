# 资源库生命周期增强 Spec

## Why
当前资源库仅支持静态的资源类型定义和条目管理，无法满足资产管理场景中「事件追踪 + 状态流转 + 通知联动」的需求（如舞台灯光设备的入库、外借、检修、报废全生命周期追踪）。需要在延续用户自定义管线思想的前提下，赋予资源库生命周期管理能力，同时与通知系统打通。

## What Changes
- ResourceType 新增 `lifecycle_config` 字段，支持管理员自定义事件类型及通知角色
- 新增 ResourceLog 模型，记录资源条目的事件时间线（入库、外借、检修、归还、报废等）
- ResourceItem.status 由最新 ResourceLog 事件自动推导，不再手动设置
- ResourceLog 创建时触发 Signal → 自动发送 Notification 给配置的通知角色
- 前端新增资源管理页面：资源列表、资源详情（含事件时间线）、事件记录操作

## Impact
- Affected specs: 资源库 (Phase 4)
- Affected code: `backend/apps/resources/models.py`, `api/serializers.py`, `api/views.py`, `api/urls.py`, `signals.py`（新增）; `frontend/src/views/ResourceList.vue`, `frontend/src/components/ResourceSelector.vue`; `designingDocument/caduceus-prd.md`, `caduceus-design.md`, `caduceus-implementation.md`

## ADDED Requirements

### Requirement: 资源类型支持自定义生命周期事件配置
系统 SHALL 允许管理员在 ResourceType 中配置该资源类型的生命周期事件类型及每个事件的通知角色。

#### Scenario: 管理员为「灯具」类型配置生命周期事件
- **WHEN** 管理员创建或编辑 ResourceType「灯具」
- **THEN** 管理员可配置 lifecycle_config，定义事件列表，如：
  - `purchase`（入库）→ 通知管理员
  - `lend_out`（外借）→ 通知管理员、检修人员
  - `return`（归还）→ 通知管理员
  - `maintenance`（检修）→ 通知管理员、检修人员
  - `scrap`（报废）→ 通知管理员

#### Scenario: 管理员不为资源类型配置生命周期事件
- **WHEN** 管理员创建 ResourceType 时不配置 lifecycle_config
- **THEN** 系统使用默认空事件列表，该资源类型无事件追踪功能

### Requirement: 资源事件日志记录
系统 SHALL 提供 ResourceLog 模型，记录资源条目上发生的每一笔事件。

#### Scenario: 记录灯具外借事件
- **WHEN** 用户对 ResourceItem「射灯 A-001」执行事件类型 `lend_out`（外借），填写摘要"借给活动组用于年会"，扩展详情 `{"借用人": "张三", "预计归还": "2026-07-10"}`
- **THEN** 系统创建 ResourceLog：`resource=射灯A-001, event_key=lend_out, operator=当前用户, summary="借给活动组...", details={...}`
- **AND** ResourceItem.status 自动更新为 `lent_out`

#### Scenario: 资源事件时间线查询
- **WHEN** 用户查看 ResourceItem 详情
- **THEN** 系统按时间倒序返回该资源的所有 ResourceLog 记录，形成事件时间线

### Requirement: 资源状态由事件自动推导
系统 SHALL 在 ResourceLog 创建后自动更新 ResourceItem.status，不再允许手动设置 status。

#### Scenario: 连续事件后状态自动更新
- **WHEN** 灯具依次经历：入库(purchase) → 外借(lend_out) → 归还(return) → 检修(maintenance)
- **THEN** ResourceItem.status 依次为：`available` → `lent_out` → `available` → `maintenance`

#### Scenario: 状态映射规则
- **WHEN** event_key 对应的 ResourceLog 被创建
- **THEN** status 映射规则为：event_key 以 `_` 连接的事件名（如 `lend_out` → `lent_out`），或在 lifecycle_config 中显式配置 status_value。若 lifecycle_config 中未配置 status_value，默认将 event_key 转为 snake_case 作为 status 值

### Requirement: 资源事件触发通知
系统 SHALL 在 ResourceLog 创建时，根据 ResourceType.lifecycle_config 中该事件的通知角色配置，自动发送站内通知。

#### Scenario: 灯具外借时通知相关角色
- **WHEN** ResourceLog(event_key=lend_out) 被创建
- **THEN** 系统查询 ResourceType.lifecycle_config 中 `lend_out` 事件的 `notify_roles`
- **AND** 向这些角色下所有用户发送 Notification，标题如"灯具「射灯 A-001」已被外借"，内容包含操作人和摘要
- **AND** 通知通过 WebSocket 实时推送

#### Scenario: 事件未配置通知角色
- **WHEN** ResourceLog 被创建但其 event_key 在 lifecycle_config 中未配置 notify_roles 或为空
- **THEN** 系统不发送通知，仅记录日志

## MODIFIED Requirements

### Requirement: ResourceItem 已有 status 字段（调整语义）
**原设计**: ResourceItem.status 为手动设置的五态枚举（available/reserved/in_use/maintenance/unavailable）
**调整后**: ResourceItem.status 由最新 ResourceLog 事件自动推导，不再接受前端手动传入。status 字段读写权限调整为只读（序列化器中设为 read_only）。

### Requirement: ResourceItem 序列化器增加 status 只读约束
ResourceItemSerializer 的 status 字段应标记为 `read_only=True`，创建/更新 ResourceItem 时忽略前端传入的 status，由系统根据 ResourceLog 最新事件自动维护。
