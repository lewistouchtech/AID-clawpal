# AID 看板整改计划

**创建时间**: 2026-04-03 20:45
**优先级**: P2
**预计耗时**: 4.5 小时

---

## 问题清单（老板反馈 20:38）

### ❌ 1. 健康数据指标未汉化
- Corn Reliability → 核心可靠性
- Success Rate → 成功率
- Active Agent Count → 活跃代理数
- 其他所有英文标签

### ❌ 2. 代理状态显示 unknown
- 状态判断逻辑不完善
- 缺少真实状态数据源

### ❌ 3. OA 平台指标未迁移
- 需要将 OA 平台的完整指标体系搬过来
- 参考现有 OA 看板设计

### ❌ 4. 多代理监控面板未融合
- 两套多代理 skill（agent-swarm-ex, agent-team-orchestration）
- 需要整合运作状况展示

### ❌ 5. 内存系统状态未展示
- Memory-Plus MCP 服务器状态
- L1/L2/L3 分级健康状况
- 优化进度和效果

---

## 整改方案

### 阶段 1: 基础修复（1 小时）
- [ ] 1.1 所有英文标签汉化
- [ ] 1.2 代理状态逻辑修复
- [ ] 1.3 数据源对接 OpenClaw API

### 阶段 2: OA 指标迁移（1 小时）
- [ ] 2.1 任务效率指标
- [ ] 2.2 成本控制指标
- [ ] 2.3 质量指标
- [ ] 2.4 进度指标

### 阶段 3: 多代理监控（1 小时）
- [ ] 3.1 agent-swarm-ex 状态展示
- [ ] 3.2 agent-team-orchestration 状态展示
- [ ] 3.3 代理协作关系图
- [ ] 3.4 任务分解可视化

### 阶段 4: 内存系统展示（1 小时）
- [ ] 4.1 Memory-Plus MCP 连接状态
- [ ] 4.2 L1/L2/L3 健康度
- [ ] 4.3 记忆存储/检索统计
- [ ] 4.4 自动修复记录

### 阶段 5: 整体优化（0.5 小时）
- [ ] 5.1 布局优化
- [ ] 5.2 数据实时更新（30 秒刷新）
- [ ] 5.3 告警机制
- [ ] 5.4 响应式设计

---

## 技术实现

### 数据源
1. **OpenClaw Sessions API**: `sessions_list`, `subagents list`
2. **Memory-Plus MCP**: `health_check`, `memory_list`
3. **OA Platform**: `oa-cli task list`, `oa-cli metrics`
4. **System Metrics**: 子代理状态、任务统计

### 前端技术
- 保持现有 HTML/CSS 架构
- 增加中文语言包
- 增加图表可视化（Chart.js 或 ECharts）
- 自动刷新机制（setInterval 30s）

### 后端扩展
- 增加 `/api/memory-health` 接口
- 增加 `/api/multi-agent-stats` 接口
- 增加 `/api/oa-metrics` 接口
- 优化现有 API 数据格式

---

## 验收标准

1. ✅ 所有标签为中文
2. ✅ 代理状态准确显示（活跃/离线/忙碌）
3. ✅ OA 指标完整展示（≥10 个核心指标）
4. ✅ 多代理监控面板融合（2 套 skill 状态）
5. ✅ 内存系统 L1/L2/L3 状态清晰展示
6. ✅ 数据实时更新（≤30 秒延迟）
7. ✅ 无报错、无卡顿

---

## 文件清单

需要修改/创建的文件：
- `dashboard.html` → 汉化 + 新功能模块
- `server.py` → 新增 API 接口
- `advanced_dashboard.html` → 同步更新
- `advanced_server.py` → 同步更新
- `README.md` → 更新文档

---

**执行顺序**: 阶段 1 → 阶段 2 → 阶段 3 → 阶段 4 → 阶段 5
**预计完成**: 2026-04-04 01:00（4.5 小时后）
