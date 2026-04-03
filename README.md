# AID-clawpal - 智能代理运营分析平台

AID (Agent Intelligence Dashboard) - OpenClaw 的内存支持与健康监控系统

## 项目简介

AID-clawpal 是一个综合性的任务看板与代理监控系统，为 OpenClaw 多代理系统提供：
- 任务管理与追踪
- 代理健康状态监控
- OA 平台指标集成
- 多代理协作监控
- 内存系统状态展示

## 功能特性

### 1. 任务看板
- 任务列表展示（待办/进行中/已完成）
- 任务优先级管理
- 任务标签分类
- 任务评论与协作

### 2. 代理监控
- 实时代理状态（运行中/空闲/忙碌/离线）
- 代理健康指标
- 活跃代理统计
- 代理性能趋势

### 3. OA 平台指标
- 任务完成率
- 平均完成时间
- 一次验收通过率
- 文件整理及时率

### 4. 多代理系统监控
- agent-swarm-ex 状态
- agent-team-orchestration 状态
- 代理协作关系可视化
- 任务分解追踪

### 5. 内存系统状态
- L1 短期记忆健康度
- L2 工作记忆健康度
- L3 长期记忆健康度
- Memory-Plus MCP 连接状态

## 项目结构

```
aid-ltd-dashboard/
├── dashboard.html          # 基础看板前端
├── server.py               # 基础看板后端
├── advanced_dashboard.html # 高级看板前端
├── advanced_server.py      # 高级看板后端
├── REFACTOR_PLAN.md        # 整改计划
├── .gitignore              # Git 忽略文件
└── README.md               # 项目说明
```

## 快速开始

### 启动基础看板

```bash
cd ~/.openclaw/projects/ongoing/aid-ltd-dashboard
python3 server.py
```

访问 http://localhost:18888

### 启动高级看板

```bash
cd ~/.openclaw/projects/ongoing/aid-ltd-dashboard
python3 advanced_server.py
```

访问 http://localhost:18889

## 技术栈

- **前端**: HTML5, CSS3, JavaScript (原生)
- **后端**: Python 3, HTTP Server
- **数据源**: oa-cli, OpenClaw Sessions API, Memory-Plus MCP
- **协议**: MCP (Model Context Protocol)

## 数据接口

### `/api/tasks` - 任务列表
返回所有任务的列表，包含状态、优先级、标签等信息。

### `/api/agents` - 代理列表
返回所有代理的状态信息，包含名称、路径、状态等。

### `/api/stats` - 系统统计
返回任务统计、代理统计等汇总数据。

### `/api/goals` - 健康指标
返回系统健康指标，包含 OA 指标、多代理状态、内存系统状态等。

## 更新日志

### v1.0.0 (2026-04-03)
- ✅ 基础看板功能
- ✅ 高级看板功能
- ✅ 英文指标汉化
- ✅ 代理状态修复
- ✅ OA 平台指标集成
- ✅ 多代理系统监控
- ✅ 内存系统状态展示

## 开发计划

- [ ] 实时数据对接（30 秒刷新）
- [ ] 可视化图表（Chart.js / ECharts）
- [ ] 告警机制
- [ ] 响应式设计优化
- [ ] 历史数据趋势分析
- [ ] 导出报告功能

## 贡献

本项目由 伊娃人工智能有限公司 开发维护。

## 许可证

MIT License

---

**最后更新**: 2026-04-03  
**版本**: 1.0.0  
**状态**: 开发中
