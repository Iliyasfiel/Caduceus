# Pipeline 字段 key 自动生成 Spec

## Why
用户不是程序员，不应手动填写"key"这种技术标识符。当前 PipelineCanvas.vue 的字段配置要求用户输入 key + label 两个字段，key 为空字符串且无自动填充，用户体验差。

## What Changes
- PipelineCanvas.vue 右侧面板移除 key 输入框
- addField() 时自动生成唯一 key（`field_0`, `field_1` 等，基于节点内字段数量）
- 已保存管线的 fields_config 中现有 key 保持不变（向后兼容）
- Label 输入框突出为主输入项，回车可直接跳到下一个输入

## Impact
- Affected specs: phase-2-pipeline-editor
- Affected code: [frontend/src/components/PipelineCanvas.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/components/PipelineCanvas.vue)（移除 key 输入框 + addField 逻辑）

## MODIFIED Requirements

### Requirement: 字段配置 UI 简化
新增字段时 SHALL 自动生成唯一 key（格式 `field_N`，其中 N 为当前节点内字段的序号），用户无需手动输入 key。

右侧编辑面板中 SHALL 移除 key 输入框，仅保留 label / type / priority_roles / is_public 四个用户可配置项。

#### Scenario: 新增字段自动生成 key
- **WHEN** 用户点击"+ 添加字段"按钮
- **THEN** 新增字段的 key 自动生成为 `field_0`（或 `field_1`/`field_2` 按当前已有字段数量递增），label 默认为空等待用户输入

#### Scenario: 加载已有管线不丢失 key
- **WHEN** 从后端加载已有管线数据
- **THEN** fields_config 中已有的 key 保持不变，新增字段时取 `Math.max(现有序号, 已有字段数)` + 1 继续编号

#### Scenario: 删除字段不影响其他 key
- **WHEN** 用户删除中间的某个字段（如 field_1）
- **THEN** 其余字段的 key 不受影响（保持原 key），新增字段时仍按当前最大序号 + 1 编号
