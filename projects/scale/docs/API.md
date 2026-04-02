# Scale - API 接口文档

**版本:** 1.0  
**Base URL:** `http://localhost:8000`

---

## 1. 接口概览

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/` | 前端页面 |
| GET | `/health` | 健康检查 |
| POST | `/eval/quick` | 创建快速测评任务 |
| GET | `/eval/status/{task_id}` | 查询任务状态 |
| WS | `/ws/eval/{task_id}` | WebSocket 实时推送 |

---

## 2. 接口详情

### 2.1 健康检查

**GET** `/health`

检查服务运行状态。

**响应:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-02T09:30:00.000000",
  "active_tasks": 0
}
```

**字段说明:**
| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | 状态: `healthy` / `degraded` |
| timestamp | string | ISO 8601 格式时间 |
| active_tasks | int | 当前活跃任务数 |

---

### 2.2 创建测评任务

**POST** `/eval/quick`

创建一个新的测评任务。

**请求体:**
```json
{
  "url": "https://mp.weixin.qq.com/s/xxxxx",
  "mode": "quick"
}
```

**字段说明:**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 文章链接，需为有效URL |
| mode | string | 否 | 测评模式: `quick`(默认) / `full` |

**响应 (200 OK):**
```json
{
  "task_id": "task_2v8x9k3m",
  "status": "pending",
  "message": "测评任务已创建，正在连接WebSocket...",
  "created_at": "2026-04-02T09:30:00.000000",
  "ws_url": "ws://localhost:8000/ws/eval/task_2v8x9k3m"
}
```

**错误响应:**
```json
// 400 Bad Request
{
  "detail": "Invalid URL format"
}

// 429 Too Many Requests
{
  "detail": "Too many active tasks, please wait"
}
```

---

### 2.3 查询任务状态

**GET** `/eval/status/{task_id}`

查询指定任务的当前状态。

**路径参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务ID |

**响应 (200 OK):**
```json
{
  "task_id": "task_2v8x9k3m",
  "status": "running",
  "progress": 45,
  "current_step": "执行测评",
  "steps": [
    {"step_id": "1", "name": "信息收集", "status": "completed", "progress": 100},
    {"step_id": "2", "name": "环境准备", "status": "completed", "progress": 100},
    {"step_id": "3", "name": "执行测评", "status": "running", "progress": 40},
    {"step_id": "4", "name": "生成报告", "status": "pending", "progress": 0}
  ],
  "result": null,
  "error": null,
  "created_at": "2026-04-02T09:30:00.000000",
  "updated_at": "2026-04-02T09:32:15.000000",
  "elapsed_seconds": 135
}
```

**状态说明:**
| 状态 | 说明 |
|------|------|
| pending | 等待开始 |
| running | 执行中 |
| completed | 已完成 |
| failed | 执行失败 |

**步骤状态:**
| 状态 | 说明 |
|------|------|
| pending | 等待执行 |
| running | 执行中 |
| completed | 已完成 |
| failed | 执行失败 |

---

### 2.4 WebSocket 实时推送

**WS** `/ws/eval/{task_id}`

建立 WebSocket 连接，实时接收任务进度和结果。

**消息类型:**

#### 2.4.1 连接成功
```json
{
  "type": "connected",
  "task_id": "task_2v8x9k3m",
  "status": "running",
  "progress": 45,
  "current_step": "执行测评",
  "steps": [...]
}
```

#### 2.4.2 进度更新
```json
{
  "type": "progress",
  "task_id": "task_2v8x9k3m",
  "status": "running",
  "progress": 60,
  "current_step": "执行测评",
  "steps": [
    {"step_id": "3", "name": "执行测评", "status": "running", "progress": 60}
  ]
}
```

#### 2.4.3 任务完成
```json
{
  "type": "completed",
  "task_id": "task_2v8x9k3m",
  "status": "completed",
  "progress": 100,
  "result": {
    "model_name": "Model-X",
    "overall_score": 85.6,
    "radar_chart": {
      "dimensions": ["知识", "推理", "代码", "数学", "语言", "安全"],
      "scores": [88, 82, 85, 79, 91, 87]
    },
    "benchmarks": [
      {"name": "MMLU", "score": 78.5, "full_mark": 100},
      {"name": "GSM8K", "score": 82.3, "full_mark": 100},
      {"name": "HumanEval", "score": 85.0, "full_mark": 100}
    ],
    "analysis": "模型在语言理解和知识问答方面表现优异...",
    "generated_at": "2026-04-02T09:35:00.000000"
  }
}
```

#### 2.4.4 任务失败
```json
{
  "type": "failed",
  "task_id": "task_2v8x9k3m",
  "status": "failed",
  "error": "GPU资源不足，无法加载模型",
  "failed_step": "环境准备"
}
```

#### 2.4.5 错误
```json
{
  "type": "error",
  "error": "任务不存在"
}
```

---

## 3. 数据模型

### 3.1 EvalRequest

```typescript
{
  url: string;        // 文章URL
  mode: "quick" | "full";  // 测评模式
}
```

### 3.2 EvalResponse

```typescript
{
  task_id: string;
  status: string;
  message: string;
  created_at: string;
  ws_url: string;
}
```

### 3.3 TaskStatus

```typescript
{
  task_id: string;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;        // 0-100
  current_step: string;
  steps: StepStatus[];
  result: EvalResult | null;
  error: string | null;
  created_at: string;
  updated_at: string;
  elapsed_seconds: number;
}
```

### 3.4 StepStatus

```typescript
{
  step_id: string;
  name: string;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;  // 0-100
}
```

### 3.5 EvalResult

```typescript
{
  model_name: string;
  overall_score: number;
  radar_chart: {
    dimensions: string[];
    scores: number[];
  };
  benchmarks: Benchmark[];
  analysis: string;
  generated_at: string;
}
```

### 3.6 Benchmark

```typescript
{
  name: string;
  score: number;
  full_mark: number;
}
```

---

## 4. 错误码

| HTTP 状态码 | 错误信息 | 说明 |
|-------------|----------|------|
| 400 | Invalid URL format | URL格式错误 |
| 404 | Task not found | 任务不存在 |
| 429 | Too many active tasks | 任务过多，请稍后再试 |
| 500 | Internal server error | 服务器内部错误 |

---

## 5. 使用示例

### 5.1 创建任务并轮询状态

```python
import requests
import time

# 创建任务
response = requests.post("http://localhost:8000/eval/quick", json={
    "url": "https://example.com/article",
    "mode": "quick"
})
data = response.json()
task_id = data["task_id"]

# 轮询状态
while True:
    status = requests.get(f"http://localhost:8000/eval/status/{task_id}").json()
    print(f"进度: {status['progress']}%, 当前步骤: {status['current_step']}")
    
    if status["status"] in ["completed", "failed"]:
        break
    
    time.sleep(2)

print(f"结果: {status['result']}")
```

### 5.2 WebSocket 实时接收

```javascript
const taskId = "task_2v8x9k3m";
const ws = new WebSocket(`ws://localhost:8000/ws/eval/${taskId}`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch (data.type) {
        case "connected":
            console.log("已连接", data);
            break;
        case "progress":
            updateProgress(data.progress, data.current_step);
            break;
        case "completed":
            displayResult(data.result);
            ws.close();
            break;
        case "failed":
            showError(data.error);
            ws.close();
            break;
    }
};
```

---

## 6. 变更日志

### v1.0 (2026-04-02)
- 初始版本
- 支持 quick/full 两种测评模式
- WebSocket 实时推送
