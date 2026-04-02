#!/usr/bin/env python3
"""
Tunnel Skill 使用示例
演示如何将本地服务快速暴露到公网
"""

import asyncio
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/tunnel/lib')

from tunnel import create_tunnel, list_tunnels, stop_all_tunnels


async def demo_basic():
    """基础用法演示"""
    print("=" * 50)
    print("示例1: 基础用法 - Cloudflare Tunnel")
    print("=" * 50)
    
    # 创建 tunnel（假设本地8000端口有服务运行）
    print("\n[1] 创建 tunnel...")
    tunnel = await create_tunnel(port=8000)
    
    print(f"✅ Tunnel 创建成功!")
    print(f"   公网地址: {tunnel.public_url}")
    print(f"   本地地址: {tunnel.local_url}")
    print(f"   进程 PID: {tunnel.pid}")
    print(f"   日志文件: {tunnel.log_file}")
    
    # 列出所有 tunnel
    print("\n[2] 列出所有活跃 tunnel...")
    tunnels = await list_tunnels()
    print(f"   共找到 {len(tunnels)} 个 tunnel")
    
    # 停止 tunnel
    print("\n[3] 停止 tunnel...")
    await tunnel.stop()
    print("   ✅ 已停止")


async def demo_with_service():
    """配合本地服务使用"""
    print("\n" + "=" * 50)
    print("示例2: 配合本地服务使用")
    print("=" * 50)
    
    import subprocess
    import time
    
    # 启动一个简单的 HTTP 服务器
    print("\n[1] 启动本地 HTTP 服务...")
    proc = subprocess.Popen(
        ["python3", "-m", "http.server", "8765"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)  # 等待服务启动
    print("   ✅ 本地服务已启动在 http://localhost:8765")
    
    try:
        # 创建 tunnel
        print("\n[2] 创建 tunnel...")
        tunnel = await create_tunnel(port=8765)
        print(f"   ✅ 公网地址: {tunnel.public_url}")
        
        print("\n[3] 现在可以通过以下地址访问本地服务:")
        print(f"   {tunnel.public_url}")
        print("\n   按 Ctrl+C 停止...")
        
        # 保持运行
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n[4] 正在清理...")
        await tunnel.stop()
        proc.terminate()
        print("   ✅ 已停止")


async def demo_different_providers():
    """对比不同 provider"""
    print("\n" + "=" * 50)
    print("示例3: 对比不同 Provider")
    print("=" * 50)
    
    # 需要本地有服务运行在 8000 端口
    print("\n假设本地服务运行在 http://localhost:8000\n")
    
    providers = [
        ("cloudflare", "Cloudflare Tunnel（推荐）"),
        ("localtunnel", "LocalTunnel"),
        # ("ngrok", "ngrok（需要 token）"),
    ]
    
    for provider, desc in providers:
        print(f"[{desc}]")
        try:
            tunnel = await create_tunnel(port=8000, provider=provider, timeout=15)
            print(f"  ✅ {tunnel.public_url}")
            await tunnel.stop()
        except Exception as e:
            print(f"  ❌ 失败: {e}")
        print()


async def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--service":
        await demo_with_service()
    elif len(sys.argv) > 1 and sys.argv[1] == "--compare":
        await demo_different_providers()
    else:
        await demo_basic()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n已取消")
        asyncio.run(stop_all_tunnels())
