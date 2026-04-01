# Claude Code 泄露代码目录结构分析报告

**报告日期**: 2026年4月1日  
**分析对象**: Kuberwastaken/claude-code (Clean-room Rust 重实现版本)  
**原始规模**: ~1,900 TypeScript 文件，~800K+ 行代码  
**Rust重实现规模**: ~53个 Rust 文件，~23,847 行代码

---

## 一、整体架构概述

Claude Code 是一个功能丰富的 AI 驱动 CLI 工具，采用**模块化多 crate 架构**进行 Clean-room 重写。整个系统分为 11 个主要 crate，每个 crate 负责特定的功能域，通过清晰的接口进行交互。

### 架构特点

| 特性 | 描述 |
|------|------|
| **语言栈** | Rust (重写实现) + 原始 TypeScript 规格说明 |
| **UI框架** | 自定义 TUI (Terminal UI)，基于类 React 的组件模型 |
| **构建工具** | Cargo (Rust 工作区) |
| **代码组织** | 工作区 (Workspace) 模式，11 个独立 crate |
| **总代码量** | ~23,847 行 Rust 代码 |

---

## 二、核心模块说明

### 1. `cli` Crate - 命令行入口
**路径**: `crates/cli/`  
**关键文件**: `src/main.rs` (1,163 行)

CLI crate 是整个应用的入口点，负责：
- 命令行参数解析
- OAuth 认证流程 (`oauth_flow.rs`)
- 应用启动初始化
- 特性标志 (feature flags) 管理

### 2. `core` Crate - 核心基础设施
**路径**: `crates/core/`

提供核心基础设施功能：
- **内存目录系统** (`memdir.rs`) - 虚拟文件系统抽象
- **OAuth 配置** (`oauth_config.rs`) - 身份验证配置管理
- **团队记忆同步** (`team_memory_sync.rs`) - 多用户状态同步
- **语音集成** (`voice.rs`) - 语音输入/输出支持
- **输出样式** (`output_styles.rs`) - 终端渲染样式
- **系统提示词** (`system_prompt.rs`) - AI 系统提示管理
- **按键绑定** (`keybindings.rs`) - 键盘快捷键系统
- **LSP 集成** (`lsp.rs`) - 语言服务器协议支持
- **数据分析** (`analytics.rs`) - 使用统计和遥测

### 3. `query` Crate - 查询引擎
**路径**: `crates/query/`

AI 查询处理的核心引擎：
- **`lib.rs`** - 查询系统主入口
- **`coordinator.rs`** - 多代理协调器
- **`auto_dream.rs`** - 自动记忆整合 (Dream System)
- **`cron_scheduler.rs`** - 定时任务调度
- **`agent_tool.rs`** - 代理工具接口
- **`compact.rs`** - 上下文压缩

### 4. `tools` Crate - 工具集
**路径**: `crates/tools/`

实现 40+ 种 AI 可调用的工具：

| 工具 | 功能 |
|------|------|
| `bash.rs` | Bash 命令执行 |
| `file_read.rs` / `file_write.rs` / `file_edit.rs` | 文件操作 |
| `web_search.rs` / `web_fetch.rs` | 网络搜索和抓取 |
| `grep_tool.rs` / `glob_tool.rs` | 代码搜索 |
| `todo_write.rs` / `tasks.rs` | 任务管理 |
| `sleep.rs` | 延迟执行 |
| `send_message.rs` | 消息发送 |
| `skill_tool.rs` / `bundled_skills.rs` | 技能系统 |
| `mcp_resources.rs` | MCP 资源访问 |
| `notebook_edit.rs` | Notebook 编辑 |
| `powershell.rs` | PowerShell 支持 |
| `worktree.rs` | 工作区管理 |
| `cron.rs` | Cron 定时任务 |
| `ask_user.rs` | 用户交互 |
| `exit_plan_mode.rs` / `enter_plan_mode.rs` | 计划模式切换 |
| `brief.rs` | 简洁输出模式 |
| `tool_search.rs` | 工具搜索 |
| `config_tool.rs` | 配置管理 |

### 5. `commands` Crate - 斜杠命令
**路径**: `crates/commands/`

- **`lib.rs`** - 命令系统框架
- **`named_commands.rs`** - 100+ 个命名命令实现

支持 100+ 个斜杠命令（如 `/help`, `/compact`, `/memory` 等）。

### 6. `buddy` Crate - 电子宠物系统
**路径**: `crates/buddy/`

完整的 Tamagotchi 风格伴侣系统：
- 18 个物种，5 个稀有度等级
- Mulberry32 PRNG 确定性随机
- ASCII 精灵渲染
- 动画系统

详见 [BUDDY 系统分析报告](./claude-code-brief-report.md)。

### 7. `tui` Crate - 终端用户界面
**路径**: `crates/tui/`

自定义终端 UI 框架：
- React 风格的组件模型
- Ink 类似的渲染器
- 键盘事件处理
- 屏幕布局管理

### 8. `bridge` Crate - 远程桥接
**路径**: `crates/bridge/`

远程会话和云同步支持：
- WebSocket/SSE 传输
- 云端会话同步
- 远程控制协议

### 9. `api` Crate - API 绑定
**路径**: `crates/api/`

- Anthropic API 客户端
- 模型调用封装
- 流式响应处理

### 10. `mcp` Crate - MCP 集成
**路径**: `crates/mcp/`

- Model Context Protocol 实现
- 外部工具集成

---

## 三、关键文件列表

### 入口与核心

| 文件路径 | 描述 | 行数 |
|---------|------|------|
| `crates/cli/src/main.rs` | 主入口点 | ~1,163 |
| `crates/cli/src/oauth_flow.rs` | OAuth 认证 | ~200+ |
| `crates/query/src/lib.rs` | 查询引擎 | ~500+ |
| `crates/query/src/coordinator.rs` | 协调器 | ~400+ |
| `crates/query/src/auto_dream.rs` | Dream 系统 | ~300+ |
| `crates/core/src/lib.rs` | 核心库 | ~300+ |

### 工具实现

| 文件路径 | 功能描述 |
|---------|---------|
| `crates/tools/src/bash.rs` | Bash 执行工具 |
| `crates/tools/src/file_read.rs` | 文件读取 |
| `crates/tools/src/file_write.rs` | 文件写入 |
| `crates/tools/src/web_search.rs` | 网络搜索 |
| `crates/tools/src/web_fetch.rs` | 网页抓取 |
| `crates/tools/src/grep_tool.rs` | Grep 搜索 |
| `crates/tools/src/sleep.rs` | 睡眠/延迟 |
| `crates/tools/src/tasks.rs` | 任务管理 |
| `crates/tools/src/cron.rs` | 定时任务 |

### BUDDY 系统

| 文件路径 | 描述 | 行数 |
|---------|------|------|
| `crates/buddy/src/lib.rs` | 完整 BUDDY 实现 | ~1,100+ |

### 规格文档

| 文件路径 | 描述 | 大小 |
|---------|------|------|
| `spec/00_overview.md` | 架构总览 | ~16 KB |
| `spec/01_core_entry_query.md` | 核心与查询 | ~72 KB |
| `spec/02_commands.md` | 命令系统 | ~70 KB |
| `spec/03_tools.md` | 工具规格 | ~66 KB |
| `spec/04_components_core_messages.md` | 组件与消息 | ~93 KB |
| `spec/11_special_systems.md` | 特殊系统 | ~68 KB |

---

## 四、特殊系统模块

### 1. KAIROS - 始终在线模式
**位置**: `crates/query/` (隐含在原始规格中)

- 后台守护进程模式
- 主动行为触发
- 15秒阻塞预算限制
- 独占工具: SendUserFile, PushNotification, SubscribePR

### 2. Dream System - 记忆整合
**位置**: `crates/query/src/auto_dream.rs`

- 后台记忆压缩引擎
- 三闸门触发系统 (时间/会话/锁)
- Forked subagent 架构

### 3. BUDDY - 电子宠物
**位置**: `crates/buddy/`

- 18物种 Tamagotchi 系统
- Mulberry32 PRNG
- ASCII 艺术渲染

### 4. ULTRAPLAN - 远程规划
**位置**: 原始 `spec/` 中描述

- 30分钟云端规划会话
- CCR (Cloud Container Runtime) 集成
- 浏览器审批流程

---

## 五、技术亮点

1. **Clean-room 工程**: 严格遵循 Phoenix Technologies v. IBM 判例，规格与实现完全分离
2. **模块化架构**: 11 个独立 crate，清晰的职责边界
3. **特性标志系统**: 编译时功能开关 (KAIROS, BUDDY, ULTRAPLAN 等)
4. **确定性随机**: Mulberry32 PRNG 确保可复现性
5. **丰富的测试**: 每个 crate 都包含单元测试

---

## 六、与原始 TypeScript 版本的差异

| 方面 | TypeScript 原版 | Rust 重写版 |
|------|----------------|-------------|
| 代码规模 | ~800K 行, ~1,900 文件 | ~24K 行, 53 文件 |
| 架构 | 单体内联 | 多 crate 工作区 |
| 入口点 | `main.tsx` (785KB) | `main.rs` (1,163 行) |
| 构建工具 | Bun | Cargo |
| 类型安全 | TypeScript | Rust (更严格) |

---

*本报告基于 Kuberwastaken/claude-code 仓库的 Clean-room Rust 重实现版本分析生成。*
