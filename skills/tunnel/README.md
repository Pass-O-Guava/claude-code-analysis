# Tunnel Skill - 内网穿透工具

一键将本地HTTP服务暴露到公网，支持 Cloudflare Tunnel、ngrok、localtunnel 多种方案。

## 快速开始

```python
from skills.tunnel import create_tunnel

# 最简单的方式 - 使用 Cloudflare Tunnel（推荐）
tunnel = await create_tunnel(port=8000)
print(f"公网地址: {tunnel.public_url}")

# 使用完毕后停止
await tunnel.stop()
```

## 支持的 Provider

| Provider | 优点 | 是否需要注册 | 适用场景 |
|----------|------|--------------|----------|
| `cloudflare` | 零配置、稳定、速度快 | ❌ 无需 | 开发演示、临时分享 |
| `ngrok` | 功能丰富、固定域名 | ✅ 需要 | 团队协作、长期项目 |
| `localtunnel` | npm快速可用 | ❌ 无需 | 快速测试 |

## 完整 API

### `create_tunnel(port, host, provider, timeout, auth_token)`

创建内网穿透隧道。

**参数：**
- `port` (int): 本地服务端口，**必填**
- `host` (str): 本地服务主机，默认 `"localhost"`
- `provider` (str): 提供商，默认 `"cloudflare"`
- `timeout` (int): 等待URL超时时间（秒），默认 `30`
- `auth_token` (str): ngrok 认证令牌（仅ngrok需要）

**返回：** `TunnelInfo` 对象

```python
@dataclass
class TunnelInfo:
    provider: str          # 提供商名称
    public_url: str        # 公网访问地址
    local_url: str         # 本地地址
    pid: int              # 进程ID
    log_file: str         # 日志文件路径
    
    async def stop() -> bool:  # 停止隧道
```

**示例：**

```python
# Cloudflare（默认）
tunnel = await create_tunnel(port=8000)

# ngrok（需要token）
tunnel = await create_tunnel(
    port=8000,
    provider="ngrok",
    auth_token="your_ngrok_token"
)

# localtunnel
tunnel = await create_tunnel(port=8000, provider="localtunnel")
```

### `list_tunnels()`

列出所有活跃的隧道。

```python
tunnels = await list_tunnels()
for t in tunnels:
    print(f"{t.provider}: {t.public_url}")
```

### `stop_all_tunnels()`

停止所有活跃的隧道。

```python
count = await stop_all_tunnels()
print(f"已停止 {count} 个隧道")
```

## 使用场景

### 场景1：快速分享本地Demo

```python
# 启动你的服务
proc = await start_my_service(port=8000)

# 创建公网访问
tunnel = await create_tunnel(port=8000)

# 分享给他人
message.send(f"Demo地址: {tunnel.public_url}")

# 使用完毕后清理
await tunnel.stop()
proc.terminate()
```

### 场景2：Webhook接收测试

```python
# 本地启动webhook服务器
tunnel = await create_tunnel(port=3000)

# 将公网地址配置到第三方服务
webhook_url = f"{tunnel.public_url}/webhook"
print(f"配置 Webhook: {webhook_url}")

# 接收回调...
```

### 场景3：移动端测试

```python
# 本地启动网站
tunnel = await create_tunnel(port=8080)

# 手机访问公网地址进行测试
print(f"手机访问: {tunnel.public_url}")
```

## CLI 使用

```bash
# 启动 tunnel
python skills/tunnel/lib/tunnel.py up 8000

# 指定 provider
python skills/tunnel/lib/tunnel.py up 8000 --provider ngrok

# 查看列表
python skills/tunnel/lib/tunnel.py list

# 停止所有
python skills/tunnel/lib/tunnel.py down
```

## 常见问题

### Q: 为什么公网地址打不开？

检查以下几点：
1. 本地服务是否正常运行：`curl http://localhost:PORT/health`
2. 防火墙是否放行
3. tunnel进程是否还在运行：`ps aux | grep cloudflared`

### Q: Cloudflare Tunnel 和 ngrok 哪个好？

- **临时演示** → Cloudflare（零配置、即开即用）
- **团队协作** → ngrok（固定域名、管理后台）
- **快速测试** → localtunnel（npm环境可用）

### Q: 隧道能持续多久？

- **Cloudflare**: 进程运行期间有效，通常几小时到几天
- **ngrok**: 免费版每次重启会更换域名
- **localtunnel**: 相对不稳定，适合短期测试

### Q: 如何固定域名？

需要付费或自建：
- ngrok Pro 支持自定义域名
- 自建 FRP 服务器实现完全控制

## 故障排查

```bash
# 1. 检查本地服务
curl http://localhost:8000/

# 2. 检查 tunnel 进程
ps aux | grep cloudflared

# 3. 查看日志
tail -f /tmp/cloudflared_tunnel_*.log

# 4. 测试公网访问
curl https://xxx.trycloudflare.com/
```

## 参考

- [SKILL.md](./SKILL.md) - 实现原理和详细设计
