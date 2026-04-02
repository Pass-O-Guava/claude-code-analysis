#!/bin/bash
# 列出所有活跃的 tunnel

cd "$(dirname "$0")/.."
python3 lib/tunnel.py list
