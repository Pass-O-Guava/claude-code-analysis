# Scale - 架构设计文档

**版本:** 1.0  
**日期:** 2026-04-02

---

## 1. 架构概览

Scale 采用**多 Agent 协作架构**，通过消息驱动的方式完成复杂的测评流程。

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端层 (Frontend)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  输入界面   │  │  进度展示   │  │      结果可视化         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP / WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         网关层 (API Gateway)                     │
│                    FastAPI + WebSocket Endpoint                  │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  任务调度器   │   │  任务状态管理   │   │  结果聚合器     │
│ EvalMaster    │   │  TaskManager    │   │  ResultBuilder  │
└───────┬───────┘   └─────────────────┘   └─────────────────┘
        │
        │ Spawn Agents
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Agent 层 (Agents)                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  │
│  │Info-       │  │  Setup-    │  │   Eval-    │  │ Report-  │  │
│  │Collector   │→ │   Agent    │→ │  Runner    │→ │  Agent   │  │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘  │
│   解析文章提取    准备GPU环境    执行基准测试    生成报告      │
│   模型信息                                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      基础设施层 (Infrastructure)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  GPU 集群   │  │  模型仓库   │  │     测评数据集          │ │
│  │  (vLLM)     │  │  (Hugging   │  │  (MMLU/GSM8K/etc)       │ │
│  │             │  │   Face)     │  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 核心组件

### 2.1 前端 (Frontend)

**技术栈:** 原生 HTML + CSS + JavaScript

**文件:** `src/index.html`

**设计原则:**
- 单文件部署，无需构建
- 响应式布局，支持移动端
- WebSocket 实时更新

**关键模块:**
```javascript
// 连接管理
WebSocketManager - 管理 WS 连接、重连机制

// 状态机
EvalStateMachine - 处理测评状态流转

// 可视化
RadarChart       - 雷达图渲染
ProgressBar      - 步骤进度条
ResultCard       - 结果卡片组件
```

### 2.2 API 网关 (API Gateway)

**技术栈:** FastAPI + Uvicorn

**文件:** `src/api.py`

**职责:**
- HTTP API 路由
- WebSocket 连接管理
- 请求验证
- 错误处理

**端点设计:**
```python
@app.post("/eval/quick")      # 创建测评任务
@app.get("/eval/status/{id}") # 查询任务状态
@app.websocket("/ws/eval/{id}") # WebSocket 推送
```

### 2.3 任务调度器 (EvalMaster)

**文件:** `src/eval_master.py`

**职责:**
- Agent 流程编排
- 状态管理
- 结果聚合

**状态机:**
```
PENDING → RUNNING → COMPLETED
              ↓
           FAILED
```

**步骤定义:**
```python
STEPS = [
    {"id": "1", "name": "信息收集", "agent": "info-collector"},
    {"id": "2", "name": "环境准备", "agent": "setup-agent"},
    {"id": "3", "name": "执行测评", "agent": "eval-runner"},
    {"id": "4", "name": "生成报告", "agent": "report-agent"},
]
```

### 2.4 Agent 层

**设计理念:**
- 每个 Agent 职责单一
- Agent 间通过消息传递
- 支持模拟模式（开发测试）和真实模式（生产）

#### Info Collector
```
输入: URL
输出: ModelInfo {name, version, architecture, capabilities}
```

#### Setup Agent
```
输入: ModelInfo
输出: Environment {gpu_id, model_path, status}
```

#### Eval Runner
```
输入: Environment, BenchmarkConfig
输出: EvalResults {scores, metrics, raw_outputs}
```

#### Report Agent
```
输入: EvalResults
输出: Report {summary, radar_data, comparison, analysis}
```

---

## 3. 数据流

### 3.1 创建测评任务

```
User → POST /eval/quick → API Gateway
                                ↓
                         TaskManager.create_task()
                                ↓
                         EvalMaster.spawn_agents()
                                ↓
                         Async Queue → Agent Workers
```

### 3.2 实时进度推送

```
Agent Worker → TaskManager.update_progress()
                    ↓
              WebSocket.broadcast()
                    ↓
              Frontend.update_ui()
```

### 3.3 结果返回

```
Agent Worker (report-agent) → TaskManager.complete()
                                   ↓
                             ResultBuilder.build()
                                   ↓
                             WebSocket.send(final_result)
                                   ↓
                             Frontend.display()
```

---

## 4. 技术选型

| 组件 | 选型 | 理由 |
|------|------|------|
| Web 框架 | FastAPI | 异步支持、自动生成文档、类型提示 |
| WS 协议 | WebSocket | 实时双向通信 |
| 前端 | Vanilla JS | 零构建、快速原型 |
| 任务队列 | Python asyncio | 轻量、足够当前需求 |
| 配置 | YAML | 可读性好、支持注释 |

---

## 5. 扩展性设计

### 5.1 新增测评数据集

```python
# eval-agents.yaml
benchmarks:
  - name: "MMLU"
    dataset: "cais/mmlu"
    metrics: ["accuracy"]
  - name: "CustomBench"  # 新增
    dataset: "org/custom"
    metrics: ["score", "latency"]
```

### 5.2 新增 Agent 类型

```python
class CustomAgent(BaseAgent):
    async def run(self, task_input: dict) -> dict:
        # 自定义逻辑
        return result
```

### 5.3 接入新模型来源

```python
# ModelSource 插件接口
class ModelSource:
    async def resolve(self, url: str) -> ModelInfo:
        """从URL解析模型信息"""
        pass
```

---

## 6. 安全考虑

### 6.1 输入校验

```python
from pydantic import HttpUrl

class EvalRequest(BaseModel):
    url: HttpUrl  # 自动校验URL格式
    mode: EvalMode
```

### 6.2 资源隔离

- 每个测评任务独立 GPU
- 超时机制防止资源占用
- 任务完成后自动清理

### 6.3 访问控制

- API 限流
- 敏感操作鉴权
- 日志审计

---

## 7. 部署架构

### 7.1 开发环境

```
本地机器
├── FastAPI (uvicorn)
├── 前端 (静态文件)
└── Mock Agents
```

### 7.2 生产环境

```
K8s Cluster
├── API Gateway (3 replicas)
├── Agent Workers (auto-scaling)
├── Redis (状态存储)
└── GPU Nodes (vLLM serving)
```

---

## 8. 监控与可观测性

### 8.1 日志

```python
import logging

logger = logging.getLogger("scale")
logger.info("Task started", extra={"task_id": tid})
```

### 8.2 指标

| 指标 | 类型 | 说明 |
|------|------|------|
| task_total | Counter | 总任务数 |
| task_duration | Histogram | 任务耗时 |
| active_tasks | Gauge | 活跃任务数 |
| agent_errors | Counter | Agent错误数 |

### 8.3 链路追踪

```python
from opentelemetry import trace

tracer = trace.get_tracer("scale")

with tracer.start_as_current_span("eval_task") as span:
    span.set_attribute("task.id", task_id)
    # ...
```
