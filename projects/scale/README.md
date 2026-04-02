# Scale - AI模型测评官

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Scale** 是一款智能大模型测评系统，基于多 Agent 协作架构，自动从文章提取模型信息、准备测评环境、执行基准测试，最终生成专业测评报告。

**体系定位：** 与 [Lodestar（AI模型选型官）](https://github.com/yourusername/lodestar) 形成完整工具链 —— Lodestar 指引方向，Scale 衡量价值。

---

## 核心特性

- 🤖 **多 Agent 协作** - 信息收集、环境准备、测评执行、报告生成，四阶段流水线
- ⚡ **实时进度推送** - WebSocket 实时推送测评进度，前端可视化展示
- 📊 **可视化报告** - 雷达图、评分卡片、详细指标，专业呈现
- 🔌 **易扩展架构** - 支持接入真实 GPU 环境或模拟数据
- 🌐 **一键公网暴露** - 集成 Cloudflare Tunnel，快速分享 Demo

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/WY/scale.git
cd scale
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

```bash
# 方式1: 直接运行
python src/api.py

# 方式2: 使用 uvicorn (推荐生产环境)
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问 Demo

浏览器打开: http://localhost:8000

或一键获取公网地址:
```bash
python scripts/expose.py
```

---

## 项目结构

```
scale/
├── src/                    # 源代码
│   ├── api.py             # FastAPI 后端主入口
│   ├── index.html         # 前端界面
│   ├── eval_master.py     # 测评任务编排器
│   └── eval-agents.yaml   # Agent 配置
├── docs/                   # 文档
│   ├── PRD.md             # 产品需求文档
│   ├── ARCHITECTURE.md    # 架构设计文档
│   └── API.md             # API 接口文档
├── scripts/                # 工具脚本
│   ├── expose.py          # 公网暴露脚本
│   └── setup.sh           # 环境初始化
├── tests/                  # 测试
├── assets/                 # 静态资源
├── requirements.txt        # Python 依赖
├── README.md              # 项目说明
└── LICENSE                # 许可证
```

---

## 工作原理

```
用户输入文章URL
       ↓
[POST /eval/quick]
       ↓
┌─────────────────────────────────────────┐
│  Phase 1: 信息收集 (info-collector)     │
│  - 解析文章提取模型信息                  │
│  - 获取模型名称、版本、能力描述          │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│  Phase 2: 环境准备 (setup-agent)        │
│  - 准备 GPU 环境                        │
│  - 下载/加载模型                        │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│  Phase 3: 执行测评 (eval-runner)        │
│  - 运行基准测试                         │
│  - 收集性能指标                         │
└─────────────────────────────────────────┘
       ↓
┌─────────────────────────────────────────┐
│  Phase 4: 生成报告 (report-agent)       │
│  - 汇总测评结果                         │
│  - 生成可视化报告                       │
└─────────────────────────────────────────┘
       ↓
WebSocket 实时推送 → 前端展示
```

---

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 前端页面 |
| `/health` | GET | 健康检查 |
| `/eval/quick` | POST | 创建快速测评任务 |
| `/eval/status/{task_id}` | GET | 查询任务状态 |
| `/ws/eval/{task_id}` | WS | WebSocket 实时推送 |

详细 API 文档见 [docs/API.md](docs/API.md)

---

## 配置说明

### 接入真实 Agent (OpenClaw)

修改 `src/api.py` 中的 `spawn_agent()` 函数:

```python
async def spawn_agent(agent_id: str, task: str, timeout: int = 300):
    result = await sessions_spawn({
        "agentId": agent_id,
        "task": task,
        "runTimeoutSeconds": timeout,
        "cleanup": "keep"
    })
    return result
```

在 `~/.openclaw/openclaw.json` 中配置 Agent:

```json
{
  "agents": {
    "list": [
      {"id": "info-collector", "description": "从文章提取模型信息"},
      {"id": "setup-agent", "description": "准备GPU环境和模型"},
      {"id": "eval-runner", "description": "执行基准测试"},
      {"id": "report-agent", "description": "生成测评报告"}
    ]
  }
}
```

---

## 开发计划

- [x] 基础架构搭建 (FastAPI + WebSocket)
- [x] 前端可视化界面
- [x] 多 Agent 流程编排
- [x] 公网暴露工具集成
- [ ] 接入真实 GPU 测评环境
- [ ] 支持更多测评数据集
- [ ] 历史测评记录管理
- [ ] 测评报告导出 (PDF)

---

## 相关项目

- [Lodestar](https://github.com/yourusername/lodestar) - AI模型选型官，智能模型推荐系统

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 致谢

本项目基于 OpenClaw 多 Agent 框架开发，感谢 OpenClaw 团队提供的强大基础设施。
