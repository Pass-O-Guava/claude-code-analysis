#!/bin/bash
# 快速启动内网穿透 Tunnel

set -e

PORT=${1:-8000}
PROVIDER=${2:-cloudflare}

echo "[tunnel] 正在启动 $PROVIDER tunnel，本地端口: $PORT..."

# 执行 Python 脚本
cd "$(dirname "$0")/.."
python3 lib/tunnel.py up "$PORT" --provider "$PROVIDER"
