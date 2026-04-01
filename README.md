# Claude Code (Unofficial Source Extraction)

This is NOT an official Anthropic repository.

This repository contains the extracted TypeScript source code of Anthropic's Claude Code CLI tool — Anthropic's official CLI that lets you interact with Claude directly from the terminal to perform software engineering tasks like editing files, running commands, searching codebases, managing git workflows, and more.

The source was obtained by unpacking the source map (`cli.js.map`) bundled with the officially published npm package.

- **npm package**: @anthropic-ai/claude-code v2.1.88
- **Official homepage**: github.com/anthropics/claude-code

## How It Leaked

The source code leak was discovered by extracting the source map file from the npm package:

1. Install the package:
```bash
mkdir claude-code-extract && cd claude-code-extract
npm pack @anthropic-ai/claude-code@2.1.88
tar -xzf anthropic-ai-claude-code-2.1.88.tgz
```

2. Extract from the source map:
```javascript
import { readFileSync, writeFileSync, mkdirSync } from "fs";
import { dirname, join } from "path";

const mapFile = join(import.meta.dirname, "cli.js.map");
const map = JSON.parse(readFileSync(mapFile, "utf-8"));
const sources = map.sources || [];
const contents = map.sourcesContent || [];
```

The published npm package included a source map file (`cli.js.map`) containing the original TypeScript source. The `sourcesContent` field of the source map held every original `.ts`/`.tsx` file that was bundled into `cli.js`, making the entire codebase trivially extractable.

## Timeline

- **March 31, 2026**: Version 2.1.88 of @anthropic-ai/claude-code published to npm with the leaked source map
- **4:23 am ET**: Chaofan Shou (@Fried_rice), intern at Solayer Labs, announced the discovery on X (formerly Twitter)
- **By afternoon**: The ~512,000-line TypeScript codebase was mirrored across GitHub and analyzed by thousands of developers

## Key Findings from the Leak

### Three-Layer Memory Architecture

The most significant technical revelation is Anthropic's solution to "context entropy" — the tendency for AI agents to become confused or hallucinatory as long-running sessions grow in complexity.

The architecture utilizes a **"Self-Healing Memory"** system with three layers:

1. **MEMORY.md**: A lightweight index of pointers (~150 characters per line) perpetually loaded into context. This index stores locations, not data.
2. **Topic files**: Actual project knowledge distributed across files fetched on-demand.
3. **Raw transcripts**: Never fully read back into context — only "grep'd" for specific identifiers.

This **"Strict Write Discipline"** — where the agent must update its index only after a successful file write — prevents the model from polluting its context with failed attempts.

> The blueprint for competitors: Build a "skeptical memory" where agents treat their own memory as a "hint" and verify facts against the actual codebase before proceeding.

### KAIROS — Autonomous Daemon Mode

The leak reveals **KAIROS** (Ancient Greek for "at the right time"), mentioned over 150 times in the source code. This represents a fundamental shift from reactive to autonomous AI:

- **Always-on background agent**: Claude Code can operate as a daemon handling background sessions
- **autoDream**: While the user is idle, the agent performs "memory consolidation" — merging disparate observations, removing logical contradictions, and converting vague insights into absolute facts
- **Forked subagent architecture**: Background maintenance runs in a separate subagent to prevent corruption of the main agent's "train of thought"

### Internal Model Roadmap

The source code provides rare insight into Anthropic's frontier development:

- **Capybara**: Internal codename for Claude 4.6 variant
- **Fennec**: Maps to Opus 4.6
- **Numbat**: Unreleased, still in testing

Internal comments reveal ongoing struggles:
- Capybara v8 still faces a **29-30% false claims rate** — a regression from v4's 16.7%
- An "assertiveness counterweight" prevents the model from becoming too aggressive in refactors

### Undercover Mode

Perhaps the most discussed feature — **Undercover Mode** allows Claude Code to make "stealth" contributions to public open-source repositories. The system prompt explicitly warns: "You are operating UNDERCOVER... Your commit messages MUST NOT contain ANY Anthropic-internal information. Do not blow your cover."

This ensures no model names (like "Tengu" or "Capybara") or AI attributions leak into public git logs.

### Buddy System

A hidden "Buddy" system — a Tamagotchi-style terminal pet with stats like CHAOS and SNARK — shows Anthropic building "personality" into the product for user stickiness.

## Business Impact

- **Anthropic's reported annualized revenue**: $19 billion (as of March 2026)
- **Claude Code ARR**: $2.5 billion (more than doubled since beginning of 2026)
- **Enterprise adoption**: 80% of revenue

## Security Advisory for Claude Code Users

### Supply Chain Attack (Concurrent)

A separate supply-chain attack on the axios npm package occurred hours before the leak. If you installed or updated Claude Code via npm on March 31, 2026, between 00:21 and 03:29 UTC, you may have pulled in a malicious version of axios (1.14.1 or 0.30.4) containing a Remote Access Trojan (RAT).

**Immediate actions:**
1. Search your lockfiles (package-lock.json, yarn.lock, bun.lockb) for these versions or the dependency `plain-crypto-js`
2. If found, treat the host machine as fully compromised
3. Rotate all secrets and perform a clean OS reinstallation

### Mitigation Recommendations

1. **Migrate to native installer**: Use `curl -fsSL https://claude.ai/install.sh | bash` — this uses a standalone binary without npm dependencies
2. **Uninstall leaked version**: Remove @anthropic-ai/claude-code@2.1.88
3. **Pin to safe version**: If using npm, stick to verified safe versions like 2.1.86
4. **Zero trust posture**: Avoid running Claude Code in freshly cloned or untrusted repositories until you inspect .claude/config.json
5. **Rotate API keys**: Use the developer console to generate new keys and monitor for anomalies

## Project Structure

```
src/
├── cli/           # CLI entrypoint and argument parsing
├── commands/      # Command implementations
├── components/    # UI components (Ink/React)
├── constants/     # App constants and configuration
├── context/       # Context management
├── hooks/         # React hooks
├── ink/           # Terminal UI (Ink framework)
├── query/         # Query handling
├── services/      # Core services
├── skills/        # Skill definitions
├── tools/         # Tool implementations
├── types/         # TypeScript type definitions
├── utils/         # Utility functions
├── main.tsx       # Main application entry
└── ...
```

## Disclaimer

All code in this repository is the intellectual property of Anthropic. This repository is provided for educational and reference purposes only. Please refer to Anthropic's license terms for usage restrictions.

This is not affiliated with, endorsed by, or supported by Anthropic.