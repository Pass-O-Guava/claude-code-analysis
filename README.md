# Claude Code 源代码泄露分析

> ⚠️ **免责声明**：本仓库是基于 [Kuberwastaken/claude-code](https://github.com/Kuberwastaken/claude-code) 的 Fork，采用 Clean-room 工程方法对 Claude Code 进行的行为分析和 Rust 重实现。不包含 Anthropic 的原始专有代码。

---

## 📋 目录

- [背景](#背景)
- [分析报告](#分析报告)
- [泄露事件概述](#泄露事件概述)
- [重大发现](#重大发现)
- [技术架构](#技术架构)
- [法律合规性](#法律合规性)

---

## 背景

2026年3月31日，Anthropic 的 AI 编程助手 **Claude Code** 遭遇严重源代码泄露。安全研究员 Chaofan Shou 在 npm 包中发现，Anthropic 意外地将包含完整源代码的 `.map` sourcemap 文件发布到了 npm 仓库。

本次 Fork 的目的是对该泄露事件进行技术分析和研究，采用 Clean-room 方法确保法律合规。

---

## 分析报告

本仓库包含以下详细分析报告：

| 报告 | 文件 | 描述 |
|------|------|------|
| **目录结构分析** | `claude-code-structure-report.md` | 整体架构、核心模块、关键文件 |
| **BUDDY 系统分析** | `claude-code-brief-report.md` | 电子宠物系统深度分析 |
| **事件摘要** | `claude-code-summary.md` | 500字核心发现概述 |
| **仓库选择分析** | `claude-code-repo-analysis.md` | 为什么选择这个版本进行 Fork |

---

## 泄露事件概述

### 泄露原因

Anthropic 在发布 npm 包时，**忘记在 `.npmignore` 中排除 `*.map` 文件**，导致 sourcemap 文件被一同发布。Sourcemap 文件本质上包含了完整的原始 TypeScript 源代码。

### 泄露规模

| 指标 | 数值 |
|------|------|
| TypeScript 文件 | ~1,900 个 |
| 代码行数 | ~513,000 行 |
| 工具数量 | 40+ |
| 斜杠命令 | 100+ |
| 入口文件 | 785KB (`main.tsx`) |

---

## 重大发现

### 🔐 内部模型代号

| 代号 | 对应模型 |
|------|---------|
| Tengu | Haiku |
| Capybara | Sonnet |
| Titan | Opus |
| Fennec | Opus 早期版本 |

### 🚀 未发布功能（44个）

#### KAIROS - 始终在线模式
- 后台守护进程，Claude 主动观察、自主决策
- 15秒阻塞预算限制
- 独占工具：SendUserFile、PushNotification、SubscribePR

#### BUDDY - 电子宠物系统
- 18个物种，5层稀有度，1%闪光率
- Mulberry32 PRNG 确定性生成
- ASCII 艺术精灵和动画
- AI 生成的灵魂（名字和性格）

#### Dream System - 记忆整合引擎
- 后台"做梦"压缩记忆
- 三闸门触发机制（24小时/5会话/锁）
- Forked subagent 架构

#### ULTRAPLAN - 远程规划
- 30分钟云端 CCR 规划会话
- Opus 4.6 深度思考
- 浏览器审批流程

### 🆕 即将发布的模型

- **Capybara v2-fast**：支持 1M 上下文窗口
- **Opus 4.7 / Sonnet 4.8**：已在内测

---

## 技术架构

### 核心模块

```
Claude Code/
├── cli/           # 命令行入口 (~1,163 行)
├── core/          # 核心基础设施
├── query/         # 查询引擎
├── tools/         # 40+ 工具实现
├── commands/      # 100+ 斜杠命令
├── buddy/         # 电子宠物系统
├── tui/           # 终端 UI 框架
├── bridge/        # 远程桥接协议
├── api/           # Anthropic API 客户端
└── mcp/           # Model Context Protocol
```

### 技术亮点

1. **自定义 React 终端渲染器** - Ink 框架
2. **多代理协调系统** - 子代理、后台代理、Swarm 模式
3. **云端同步架构** - Bridge 协议 (WebSocket/SSE)
4. **完善的工具生态** - 文件、搜索、Web、任务全覆盖

---

## 法律合规性

本 Fork 采用 **Clean-room 工程方法**：

1. **规格阶段**：AI 分析原始代码，生成行为规格（不含代码）
2. **实现阶段**：另一 AI 仅根据规格重写，从不参考原始代码

### 法律先例支持

- **Phoenix Technologies v. IBM (1984)**：Clean-room BIOS 重写合法
- **Baker v. Selden (1879)**：版权保护表达而非思想

### 为何选择这个版本

| 仓库 | 法律风险 | 可用性 | 分析价值 |
|------|---------|-------|---------|
| 原始 sourcemap | **高** | 低（已被 DMCA 下架） | 高 |
| **Clean-room 重写** | **低** | **高** | **高** |
| 口头描述 | 低 | 高 | 低 |

---

## 快速开始

```bash
# 克隆本仓库
git clone https://github.com/Pass-O-Guava/claude-code-analysis.git
cd claude-code-analysis

# 查看分析报告
cat claude-code-summary.md
cat claude-code-structure-report.md
cat claude-code-brief-report.md
cat claude-code-repo-analysis.md
```

---

## 参考资源

- **原始分析仓库**: https://github.com/Kuberwastaken/claude-code
- **Clean-room 法律先例**: Phoenix Technologies v. IBM, 1984
- **版权原则**: Baker v. Selden, 1879
- **合理使用**: 17 U.S.C. § 107

---

## 作者

分析报告由 AI Agent 团队生成：
- **Research Agent** - 仓库调研和信息收集
- **Dev Agent** - 技术报告撰写

Fork 所有者: [Pass-O-Guava](https://github.com/Pass-O-Guava)

---

*本仓库内容基于公开可得的 Clean-room 重实现版本生成，符合合理使用原则。*
