#!/usr/bin/env python3
"""
使用 Tunnel Skill 暴露测评 Demo 的完整示例

这是从今天的实际操作中提取的最佳实践
"""

import asyncio
import subprocess
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/tunnel/lib')

from tunnel import create_tunnel, stop_all_tunnels


async def expose_eval_system():
    """
    暴露测评系统到公网的完整流程
    
    场景：eval-system 服务已经在 http://localhost:8000 运行
    """
    print("=" * 60)
    print("🚀 使用 Tunnel Skill 暴露测评 Demo")
    print("=" * 60)
    
    # 1. 确认本地服务运行
    print("\n[1/4] 检查本地服务...")
    import urllib.request
    try:
        urllib.request.urlopen("http://localhost:8000/health", timeout=2)
        print("   ✅ 本地服务运行正常")
    except:
        print("   ❌ 本地服务未启动，请先运行: python api.py")
        return
    
    # 2. 创建 Cloudflare Tunnel
    print("\n[2/4] 创建 Cloudflare Tunnel...")
    print("   正在下载/检查 cloudflared...")
    
    try:
        tunnel = await create_tunnel(
            port=8000,
            provider="cloudflare",
            timeout=30
        )
        print(f"   ✅ Tunnel 创建成功!")
        print(f"   🌐 公网地址: {tunnel.public_url}")
        
    except Exception as e:
        print(f"   ❌ 创建失败: {e}")
        return
    
    # 3. 验证公网访问
    print("\n[3/4] 验证公网访问...")
    try:
        import urllib.request
        req = urllib.request.urlopen(f"{tunnel.public_url}/health", timeout=10)
        data = req.read().decode()
        if '"status":"healthy"' in data:
            print("   ✅ 公网访问正常")
        else:
            print(f"   ⚠️ 响应异常: {data[:100]}")
    except Exception as e:
        print(f"   ⚠️ 验证失败: {e}")
    
    # 4. 保持运行
    print("\n[4/4] Tunnel 运行中...")
    print("-" * 60)
    print(f"测评 Demo 已可通过公网访问:")
    print(f"  🔗 {tunnel.public_url}")
    print(f"  🔗 {tunnel.public_url}/index.html")
    print("-" * 60)
    print(f"\n进程 PID: {tunnel.pid}")
    print(f"日志文件: {tunnel.log_file}")
    print("\n按 Ctrl+C 停止...")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n\n正在停止...")
        await tunnel.stop()
        print("✅ 已停止")


async def quick_expose(port: int = 8000):
    """
    极简用法：一行代码暴露服务
    """
    tunnel = await create_tunnel(port=port)
    print(f"公网地址: {tunnel.public_url}")
    return tunnel


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # 极简模式
        tunnel = asyncio.run(quick_expose(8000))
        print(f"\nPID: {tunnel.pid}")
        print("手动停止: kill", tunnel.pid)
    else:
        # 完整演示
        try:
            asyncio.run(expose_eval_system())
        except KeyboardInterrupt:
            print("\n已取消")
            asyncio.run(stop_all_tunnels())
