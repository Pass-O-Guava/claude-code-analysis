#!/bin/bash
# 停止所有 tunnel

echo "[tunnel] 正在停止所有 tunnel..."

cd "$(dirname "$0")/.."
python3 lib/tunnel.py down
