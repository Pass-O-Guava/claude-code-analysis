#!/usr/bin/env python3
"""
内网穿透 Tunnel 封装库
支持 Cloudflare Tunnel、ngrok、localtunnel
"""

import asyncio
import os
import re
import signal
import subprocess
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Dict
# import aiohttp  # 可选依赖


@dataclass
class TunnelInfo:
    """隧道信息"""
    provider: str
    public_url: str
    local_url: str
    pid: int
    log_file: str
    created_at: float = field(default_factory=time.time)
    _stop_fn: Optional[Callable] = None
    
    async def stop(self) -> bool:
        """停止此隧道"""
        if self._stop_fn:
            return await self._stop_fn()
        try:
            os.kill(self.pid, signal.SIGTERM)
            return True
        except ProcessLookupError:
            return False


class TunnelManager:
    """隧道管理器"""
    
    PROVIDERS = {
        "cloudflare": {
            "binary": "cloudflared",
            "download_url": "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64",
            "url_pattern": r'https://[a-zA-Z0-9-]+\.trycloudflare\.com',
        },
        "ngrok": {
            "binary": "ngrok",
            "download_url": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz",
            "url_pattern": r'https://[a-zA-Z0-9-]+\.ngrok\.io',
            "needs_auth": True,
        },
        "localtunnel": {
            "binary": "npx",
            "url_pattern": r'https://[a-zA-Z0-9-]+\.loca\.lt',
        }
    }
    
    def __init__(self, cache_dir: str = "/tmp"):
        self.cache_dir = cache_dir
        self._binaries: Dict[str, str] = {}
    
    async def _ensure_binary(self, provider: str) -> str:
        """确保二进制文件可用"""
        if provider in self._binaries:
            return self._binaries[provider]
        
        config = self.PROVIDERS[provider]
        binary_name = config["binary"]
        
        # 检查系统PATH
        if provider == "localtunnel":
            # localtunnel 使用 npx
            self._binaries[provider] = "npx"
            return "npx"
        
        # 检查已下载的二进制
        cached_path = os.path.join(self.cache_dir, binary_name)
        if os.path.exists(cached_path) and os.access(cached_path, os.X_OK):
            self._binaries[provider] = cached_path
            return cached_path
        
        # 下载二进制
        print(f"[Tunnel] 下载 {provider} 二进制文件...")
        await self._download_binary(provider, cached_path)
        self._binaries[provider] = cached_path
        return cached_path
    
    async def _download_binary(self, provider: str, dest_path: str):
        """下载二进制文件"""
        config = self.PROVIDERS[provider]
        url = config["download_url"]
        
        if provider == "cloudflare":
            # 直接下载二进制
            proc = await asyncio.create_subprocess_exec(
                "curl", "-fsSL", "-o", dest_path, url,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.wait()
            os.chmod(dest_path, 0o755)
            
        elif provider == "ngrok":
            # 下载并解压
            tgz_path = f"{dest_path}.tgz"
            proc = await asyncio.create_subprocess_exec(
                "curl", "-fsSL", "-o", tgz_path, url,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.wait()
            
            proc = await asyncio.create_subprocess_exec(
                "tar", "-xzf", tgz_path, "-C", self.cache_dir,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.wait()
            os.remove(tgz_path)
    
    async def create_tunnel(
        self,
        port: int,
        host: str = "localhost",
        provider: str = "cloudflare",
        timeout: int = 30,
        auth_token: Optional[str] = None
    ) -> TunnelInfo:
        """创建内网穿透隧道"""
        
        if provider not in self.PROVIDERS:
            raise ValueError(f"不支持的 provider: {provider}")
        
        config = self.PROVIDERS[provider]
        binary = await self._ensure_binary(provider)
        
        # 构建命令
        if provider == "cloudflare":
            cmd = [binary, "tunnel", "--url", f"http://{host}:{port}"]
        elif provider == "ngrok":
            if config.get("needs_auth") and not auth_token:
                raise ValueError("ngrok 需要提供 auth_token")
            cmd = [binary, "http", str(port), f"--host-header={host}"]
            if auth_token:
                cmd.extend(["--authtoken", auth_token])
        elif provider == "localtunnel":
            cmd = [binary, "--yes", "localtunnel", "--port", str(port)]
        
        # 启动进程
        log_file = os.path.join(self.cache_dir, f"{provider}_tunnel_{int(time.time())}.log")
        
        with open(log_file, "w") as log:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=log,
                stderr=subprocess.STDOUT
            )
        
        # 等待并提取公网URL
        public_url = await self._wait_for_url(log_file, config["url_pattern"], timeout)
        
        if not public_url:
            proc.terminate()
            raise RuntimeError(f"无法在 {timeout} 秒内获取公网地址，请检查日志: {log_file}")
        
        info = TunnelInfo(
            provider=provider,
            public_url=public_url,
            local_url=f"http://{host}:{port}",
            pid=proc.pid,
            log_file=log_file
        )
        
        # 绑定停止函数
        async def stop_fn():
            try:
                proc.terminate()
                await asyncio.wait_for(proc.wait(), timeout=5)
            except asyncio.TimeoutError:
                proc.kill()
            return True
        
        info._stop_fn = stop_fn
        return info
    
    async def _wait_for_url(self, log_file: str, pattern: str, timeout: int) -> Optional[str]:
        """从日志文件中等待URL出现"""
        start_time = time.time()
        regex = re.compile(pattern)
        
        while time.time() - start_time < timeout:
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    content = f.read()
                    match = regex.search(content)
                    if match:
                        return match.group(0)
            await asyncio.sleep(0.5)
        
        return None
    
    async def list_tunnels(self) -> List[TunnelInfo]:
        """列出所有活跃的 tunnel"""
        tunnels = []
        
        for provider, config in self.PROVIDERS.items():
            binary_name = config["binary"]
            if provider == "localtunnel":
                binary_name = "localtunnel"
            
            # 查找进程
            proc = await asyncio.create_subprocess_exec(
                "pgrep", "-f", binary_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL
            )
            stdout, _ = await proc.communicate()
            
            for pid_str in stdout.decode().strip().split("\n"):
                if pid_str:
                    try:
                        pid = int(pid_str)
                        # 获取进程信息
                        info = await self._get_tunnel_info(pid)
                        if info:
                            tunnels.append(info)
                    except ValueError:
                        pass
        
        return tunnels
    
    async def _get_tunnel_info(self, pid: int) -> Optional[TunnelInfo]:
        """获取 tunnel 信息（从进程信息推断）"""
        # 简化实现：实际使用时可从持久化存储读取
        return None
    
    async def stop_all(self) -> int:
        """停止所有 tunnel"""
        count = 0
        for provider, config in self.PROVIDERS.items():
            binary_name = config["binary"]
            if provider == "localtunnel":
                binary_name = "localtunnel"
            
            proc = await asyncio.create_subprocess_exec(
                "pkill", "-f", binary_name,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await proc.wait()
            count += 1
        
        return count


# 便捷函数
_manager = None

async def get_manager() -> TunnelManager:
    """获取全局管理器实例"""
    global _manager
    if _manager is None:
        _manager = TunnelManager()
    return _manager


async def create_tunnel(
    port: int,
    host: str = "localhost",
    provider: str = "cloudflare",
    timeout: int = 30,
    auth_token: Optional[str] = None
) -> TunnelInfo:
    """快速创建隧道"""
    manager = await get_manager()
    return await manager.create_tunnel(
        port=port,
        host=host,
        provider=provider,
        timeout=timeout,
        auth_token=auth_token
    )


async def list_tunnels() -> List[TunnelInfo]:
    """列出所有隧道"""
    manager = await get_manager()
    return await manager.list_tunnels()


async def stop_all_tunnels() -> int:
    """停止所有隧道"""
    manager = await get_manager()
    return await manager.stop_all()


# CLI 入口
if __name__ == "__main__":
    import sys
    
    async def main():
        if len(sys.argv) < 2:
            print("Usage: python tunnel.py <up|list|down> [port] [options]")
            sys.exit(1)
        
        cmd = sys.argv[1]
        
        if cmd == "up":
            if len(sys.argv) < 3:
                print("Usage: python tunnel.py up <port> [--provider cloudflare|ngrok|localtunnel]")
                sys.exit(1)
            
            port = int(sys.argv[2])
            provider = "cloudflare"
            
            # 解析选项
            for i, arg in enumerate(sys.argv[3:], 3):
                if arg == "--provider" and i + 1 < len(sys.argv):
                    provider = sys.argv[i + 1]
            
            print(f"[Tunnel] 正在启动 {provider} tunnel，本地端口: {port}...")
            
            try:
                tunnel = await create_tunnel(port=port, provider=provider)
                print(f"✅ Tunnel 已启动!")
                print(f"   公网地址: {tunnel.public_url}")
                print(f"   本地地址: {tunnel.local_url}")
                print(f"   进程 PID: {tunnel.pid}")
                print(f"   日志文件: {tunnel.log_file}")
                print(f"\n按 Ctrl+C 停止...")
                
                # 保持运行
                while True:
                    await asyncio.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n[Tunnel] 正在停止...")
                await tunnel.stop()
                print("✅ 已停止")
                
        elif cmd == "list":
            tunnels = await list_tunnels()
            if not tunnels:
                print("没有活跃的 tunnel")
            else:
                print(f"找到 {len(tunnels)} 个活跃的 tunnel:")
                for t in tunnels:
                    print(f"  - {t.provider}: {t.public_url} (PID: {t.pid})")
                    
        elif cmd == "down":
            count = await stop_all_tunnels()
            print(f"✅ 已停止 {count} 个 tunnel")
            
        else:
            print(f"未知命令: {cmd}")
            sys.exit(1)
    
    asyncio.run(main())
