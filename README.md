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