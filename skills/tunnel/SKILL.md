# 内网穿透 Skill - 设计文档

## 概述

将本地HTTP服务快速暴露到公网，支持多种tunnel方案，默认使用Cloudflare Tunnel（零配置、免注册）。

## 核心原理

```
用户浏览器 → Cloudflare边缘节点 ←──→ cloudflared进程 ←──→ 本地服务
                              (加密隧道)            (本地回环)
```

## 实现步骤详解

### 1. 前置检查
- 确认本地服务端口可访问：`curl http://localhost:PORT/health`
- 检查防火墙/安全组是否放行（如使用IP直连）
- 确认公网IP：`curl https://api.ipify.org`

### 2. 方案选择矩阵

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **Cloudflare Tunnel** | 零配置、免注册、稳定 | 域名随机 | 开发演示、临时分享 |
| ngrok | 功能丰富、有管理后台 | 需auth token | 长期项目、团队协作 |
| localtunnel | npm一键安装 | 稳定性一般 | 快速测试 |
| 自建FRP | 完全可控 | 需服务器 | 生产环境 |

### 3. Cloudflare Tunnel 实施步骤

```bash
# 1. 下载 cloudflared (Linux AMD64)
curl -fsSL -o /tmp/cloudflared \
  https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64

# 2. 赋予执行权限
chmod +x /tmp/cloudflared

# 3. 验证安装
/tmp/cloudflared version

# 4. 启动 tunnel (后台运行)
nohup /tmp/cloudflared tunnel --url http://localhost:8000 \
  > /tmp/cf_tunnel.log 2>&1 &

# 5. 提取公网地址 (约5-10秒后)
sleep 6
grep -oE 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' /tmp/cf_tunnel.log
```

### 4. 容易出错的细节

#### ❌ 错误1：Mac版ngrok在Linux运行
```
/usr/bin/ngrok: 1: Syntax error: ")" unexpected
```
**原因**：node_modules里的ngrok是darwin二进制文件  
**解决**：下载对应平台的二进制文件

#### ❌ 错误2：npm包的cloudflared权限问题
```
Error: spawn /usr/lib/node_modules/cloudflared/bin/cloudflared EACCES
```
**原因**：npm安装的cloudflared可能是脚本包装器  
**解决**：直接下载官方二进制文件

#### ❌ 错误3：文件正在下载时被访问
```
Text file busy
```
**原因**：curl还在写入文件，同时尝试执行  
**解决**：确保下载完成后再chmod +x

#### ❌ 错误4：防火墙/安全组拦截
```
nc: connect to xxx port 8000 failed: Connection timed out
```
**原因**：云服务器安全组未放行端口  
**解决**：使用tunnel方案绕过，或配置安全组规则

#### ❌ 错误5：服务未正确托管静态文件
```
{"detail":"Not Found"}  # 访问/返回API响应而非前端页面
```
**原因**：FastAPI未配置静态文件路由  
**解决**：
```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))
```

## 封装 Skill 设计

### 目录结构
```
tunnel/
├── SKILL.md              # 本文档
├── README.md             # 用户使用指南
├── scripts/
│   ├── setup.sh          # 安装 cloudflared
│   ├── start.sh          # 启动 tunnel
│   └── stop.sh           # 停止所有 tunnel
└── lib/
    └── tunnel.py         # Python封装库
```

### 核心接口设计

```python
async def create_tunnel(
    local_port: int,
    local_host: str = "localhost",
    provider: str = "cloudflare",  # cloudflare | ngrok | localtunnel
    timeout: int = 30
) -> TunnelInfo:
    """
    创建内网穿透隧道
    
    Returns:
        TunnelInfo: {
            public_url: str,      # 公网访问地址
            local_url: str,       # 本地地址
            pid: int,             # 进程ID
            log_file: str,        # 日志路径
            stop: Callable        # 停止函数
        }
    """

async def list_tunnels() -> List[TunnelInfo]:
    """列出所有活跃的 tunnel"""

async def stop_tunnel(pid: int) -> bool:
    """停止指定 tunnel"""

async def stop_all_tunnels() -> int:
    """停止所有 tunnel，返回停止数量"""
```

### CLI 命令

```bash
# 快速启动
openclaw tunnel up 8000

# 指定提供商
openclaw tunnel up 8000 --provider ngrok --token xxx

# 查看列表
openclaw tunnel list

# 停止指定
openclaw tunnel stop <pid>

# 停止全部
openclaw tunnel down
```

## 使用示例

### 场景1：快速分享本地Demo
```python
from skills.tunnel import create_tunnel

# 启动 tunnel
tunnel = await create_tunnel(port=8000)
print(f"公网地址: {tunnel.public_url}")

# 使用完毕后停止
await tunnel.stop()
```

### 场景2：配合其他服务自动暴露
```python
# 启动本地服务
proc = await spawn_service(port=8000)

# 自动创建 tunnel
tunnel = await create_tunnel(port=8000)

# 返回给用户
return {
    "local": "http://localhost:8000",
    "public": tunnel.public_url
}
```

## 实现代码参考

见 `lib/tunnel.py` 完整实现。

## 相关工具对比

| 特性 | Cloudflare | ngrok | LocalTunnel | FRP |
|------|-----------|-------|-------------|-----|
| 注册要求 | ❌ 无需 | ✅ 需要 | ❌ 无需 | ❌ 无需 |
| 自定义域名 | ✅ 付费 | ✅ 付费 | ❌ | ✅ 自建 |
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 速度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 开源 | ✅ | ❌ | ✅ | ✅ |
| 自托管 | ❌ | ❌ | ❌ | ✅ |

## 最佳实践

1. **开发演示**：Cloudflare Tunnel（最简单）
2. **团队协作**：ngrok + 固定域名
3. **生产环境**：自建FRP或Nginx反向代理
4. **临时分享**：localtunnel（npm快速可用）

## 故障排查

```bash
# 1. 检查服务是否在运行
curl http://localhost:PORT/health

# 2. 检查 tunnel 进程
ps aux | grep cloudflared

# 3. 查看日志
tail -f /tmp/cf_tunnel.log

# 4. 测试公网地址
curl https://xxx.trycloudflare.com/health

# 5. 端口占用检查
lsof -i :PORT || ss -tlnp | grep PORT
```

## 安全注意

- Tunnel 是临时性的，进程结束后公网地址失效
- 不要在生产环境依赖临时 tunnel
- 敏感服务建议加认证（Basic Auth或Token）
- Cloudflare Tunnel 默认有DDoS保护

## 参考链接

- Cloudflare Tunnel: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/
- ngrok: https://ngrok.com/
- LocalTunnel: https://localtunnel.github.io/www/
- FRP: https://github.com/fatedier/frp
