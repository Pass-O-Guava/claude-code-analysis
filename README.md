# IMPORTANT NOTICE - UPDATE

This repository does not hold a copy of the proprietary Claude Code typescript source code.
This is a clean-room Rust reimplementation of Claude Code's behavior.

The process was explicitly two-phase:

Specification [`spec/`](https://github.com/kuberwastaken/claude-code/tree/main/spec) - An AI agent analyzed the source and produced exhaustive behavioral specifications and improvements, deviated from the original: architecture, data flows, tool contracts, system designs. No source code was carried forward.

Implementation [`src-rust/`](https://github.com/kuberwastaken/claude-code/tree/main/src-rust)- A separate AI agent implemented from the spec alone, never referencing the original TypeScript. The output is idiomatic Rust that reproduces the behavior, not the expression.

This mirrors the legal precedent established by Phoenix Technologies v. IBM (1984) — clean-room engineering of the BIOS — and the principle from Baker v. Selden (1879) that copyright protects expression, not ideas or behavior.

The analysis below is commentary on publicly available software, protected under fair use (17 U.S.C. § 107). Code excerpts are quoted to illustrate technical points from a public source - no unauthorized access was involved in this process or research.

---

# Claude Code Analysis & Skills Repository

This repository contains:
1. **Analysis reports** of Claude Code's architecture and behavior
2. **Reusable skills** for OpenClaw/Claude Code agents
3. **Project documentation** for AI model evaluation tools

---

## 📁 Repository Structure

```
.
├── README.md                           # This file
├── spec/                               # Claude Code behavioral specifications
├── src-rust/                           # Rust reimplementation
├── public/                             # Static assets
├── skills/                             # 🔧 Reusable skills for agents
│   └── tunnel/                         # 内网穿透工具 (Network tunneling)
│       ├── SKILL.md                    # Design documentation
│       ├── README.md                   # User guide
│       ├── lib/tunnel.py               # Core implementation
│       ├── example.py                  # Usage examples
│       ├── demo_eval_system.py         # Demo integration
│       └── scripts/                    # CLI scripts (up.sh, down.sh, list.sh)
├── projects/                           # 📊 Project documentations
│   └── scale/                          # Scale - AI模型测评官
│       ├── NAMING.md                   # Product naming rationale
│       ├── README.md                   # Project overview
│       └── docs/                       # Detailed documentation
│           ├── PRD.md                  # Product Requirements Document
│           ├── ARCHITECTURE.md         # System architecture
│           └── API.md                  # API reference
└── [analysis reports]                  # Claude Code analysis
    ├── claude-code-brief-report.md
    ├── claude-code-repo-analysis.md
    ├── claude-code-structure-report.md
    └── claude-code-summary.md
```

---

## 🛠️ Skills

### Tunnel Skill - 内网穿透工具

A reusable skill for exposing local HTTP services to the public internet with zero configuration.

**Features:**
- 🚀 **Zero-config** with Cloudflare Tunnel (default)
- 🔌 Multiple providers: Cloudflare, ngrok, localtunnel
- 🐍 Python API and CLI interface
- 📦 Automatic binary download and management

**Quick Start:**
```python
from skills.tunnel import create_tunnel

# Expose local service on port 8000
tunnel = await create_tunnel(port=8000)
print(f"Public URL: {tunnel.public_url}")
# → https://xxx.trycloudflare.com

# Stop when done
await tunnel.stop()
```

**Documentation:** [skills/tunnel/README.md](skills/tunnel/README.md)  
**Design Doc:** [skills/tunnel/SKILL.md](skills/tunnel/SKILL.md)

---

## 📊 Projects

### Scale - AI模型测评官

**Scale** is an intelligent LLM evaluation system that automatically:
1. Extracts model information from articles
2. Prepares evaluation environments
3. Runs benchmark tests (MMLU, GSM8K, HumanEval, etc.)
4. Generates professional evaluation reports

**Product Matrix:**
| Product | Chinese Name | Purpose |
|---------|--------------|---------|
| **Lodestar** | AI模型选型官 | Guides direction |
| **Scale** | AI模型测评官 | Measures value |

**Key Features:**
- 🤖 Multi-Agent collaboration architecture
- ⚡ Real-time WebSocket progress updates
- 📊 Visual reports with radar charts
- 🔌 Easy-to-extend plugin system
- 🌐 One-click public exposure

**Documentation:**
- [Naming Rationale](projects/scale/NAMING.md) - Why "Scale"?
- [Product Requirements](projects/scale/docs/PRD.md)
- [Architecture Design](projects/scale/docs/ARCHITECTURE.md)
- [API Documentation](projects/scale/docs/API.md)

**Source Code:** [Pass-O-Guava/scale](https://github.com/Pass-O-Guava/scale) (Private)

---

## 🔍 Original Analysis

The following sections contain the original analysis of Claude Code's architecture:

---

# Claude Code's Entire Source Code Got Leaked via a Sourcemap in npm, Let's Talk About It

## Technical Breakdown

> **PS:** I've also published this [breakdown on my blog](https://kuber.studio/blog/AI/Claude-Code's-Entire-Source-Code-Got-Leaked-via-a-Sourcemap-in-npm,-Let's-Talk-About-it) with a better reading experience and UX :)

Earlier today (March 31st, 2026) - Chaofan Shou on X discovered something that Anthropic probably didn't want the world to see: the **entire source code** of Claude Code, Anthropic's official AI coding CLI, was sitting in plain sight on the npm registry via a sourcemap file bundled into the published package.

[![The tweet announcing the leak](https://raw.githubusercontent.com/kuberwastaken/claude-code/main/public/leak-tweet.png)](https://raw.githubusercontent.com/kuberwastaken/claude-code/main/public/leak-tweet.png)

This repository is a backup of that leaked source, and this README is a full breakdown of what's in it, how the leak happened and most importantly, the things we now know that were never meant to be public.

Let's get into it.

## How Did This Even Happen?

This is the part that honestly made me go "...really?"

When you publish a JavaScript/TypeScript package to npm, the build toolchain often generates **source map files** (`.map` files). These files are a bridge between the minified/bundled production code and the original source, they exist so that when something crashes in production the stack trace can point you to the *actual* line of code in the *original* file, not some unintelligible line 1, column 48293 of a minified blob.

But the fun part is **source maps contain the original source code**. The actual, literal, raw source code, embedded as strings inside a JSON file.

The structure of a `.map` file looks something like this:

```json
{
  "version": 3,
  "sources": ["../src/main.tsx", "../src/tools/BashTool.ts", "..."],
  "sourcesContent": ["// The ENTIRE original source code of each file", "..."],
  "mappings": "AAAA,SAAS,OAAO..."
}
```

That `sourcesContent` array? That's everything.
Every file. Every comment. Every internal constant. Every system prompt. All of it, sitting right there in a JSON file that npm happily serves to anyone who runs `npm pack` or even just browses the package contents.

This is not a novel attack vector. It's happened before and honestly it'll happen again.

The mistake is almost always the same: someone forgets to add `*.map` to their `.npmignore` or doesn't configure their bundler to skip source map generation for production builds. With Bun's bundler (which Claude Code uses), source maps are generated by default unless you explicitly turn them off.

[![Claude Code source files exposed in npm package](https://raw.githubusercontent.com/kuberwastaken/claude-code/main/public/claude-files.png)](https://raw.githubusercontent.com/kuberwastaken/claude-code/main/public/claude-files.png)

The funniest part is, there's an entire system called ["Undercover Mode"](#undercover-mode--do-not-blow-your-cover) specifically designed to prevent Anthropic's internal information from leaking.

They built a whole subsystem to stop their AI from accidentally revealing internal codenames in git commits... and then shipped the entire source in a `.map` file, likely by Claude.

---

## What's Claude Under The Hood?

If you've been living under a rock, Claude Code is Anthropic's official CLI tool for coding with Claude and the most popular AI coding agent.

From the outside, it looks like a polished but relatively simple CLI.

From the inside, It's a **785KB [`main.tsx`](https://github.com/kuberwastaken/claude-code/blob/main/src-rust/crates/cli/src/main.rs)** entry point, a custom React terminal renderer, 40+ tools, a multi-agent orchestration system, a background memory consolidation engine called "dream," and much more

Enough yapping, here's some parts about the source code that are genuinely cool that I found after an afternoon deep dive:

---

## BUDDY - A Tamagotchi Inside Your Terminal

I am not making this up.

Claude Code has a full **Tamagotchi-style companion pet system** called "Buddy." A **deterministic gacha system** with species rarity, shiny variants, procedurally generated stats, and a soul description written by Claude on first hatch like OpenClaw.

The entire thing lives in [`buddy/`](https://github.com/kuberwastaken/claude-code/tree/main/src-rust/crates) and is gated behind the `BUDDY` compile-time feature flag.

### The Gacha System

Your buddy's species is determined by a **Mulberry32 PRNG**, a fast 32-bit pseudo-random number generator seeded from your `userId` hash with the salt `'friend-2026-401'`:

```typescript
// Mulberry32 PRNG - deterministic, reproducible per-user
function mulberry32(seed: number): () => number {
  return function() {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    var t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  }
}
```
