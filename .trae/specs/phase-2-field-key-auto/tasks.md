# Tasks

- [x] Task 1: PipelineCanvas.vue 移除 key 输入框 + addField 自动生成 key
  - [x] 模板中移除 field key 的 `<input>` 行
  - [x] 修改 `addField()` 函数：自动生成 key，取已有 field_N 最大序号 + 1（兼容已有管线数据）
  - [x] 删除字段时不影响其他字段的 key（不做重编号）

# Task Dependencies
- 无外部依赖，仅修改 PipelineCanvas.vue 一个文件
