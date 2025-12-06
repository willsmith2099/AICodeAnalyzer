# 远程 Ollama 配置说明

## 概述

本配置使用宿主机上运行的 Ollama 服务，而不是在 Docker 容器中运行 Ollama。这样可以：
- 节省磁盘空间（Ollama 镜像约 2GB）
- 避免重复下载模型
- 提高性能（直接访问宿主机服务）

## 前置条件

### 1. 确保宿主机 Ollama 服务正在运行

```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 如果未运行，启动 Ollama
ollama serve
```

### 2. 确保已安装所需模型

```bash
# 列出已安装的模型
ollama list

# 如果没有 qwen2.5:0.5b，拉取模型
ollama pull qwen2.5:0.5b
```

## 配置说明

### Docker Compose 配置

在 `docker-compose.yml` 中，我们使用了以下配置：

```yaml
environment:
  - OLLAMA_API_URL=http://host.docker.internal:11434

extra_hosts:
  - "host.docker.internal:host-gateway"
```

**说明：**
- `host.docker.internal` 是 Docker 提供的特殊 DNS 名称，指向宿主机
- `extra_hosts` 确保容器可以解析这个主机名
- 端口 `11434` 是 Ollama 的默认端口

## 使用方法

### 1. 启动宿主机 Ollama 服务

```bash
# 在宿主机上启动 Ollama（如果未运行）
ollama serve
```

### 2. 启动 Docker 服务

```bash
cd docker
docker-compose up -d
```

### 3. 验证连接

```bash
# 检查服务状态
docker-compose ps

# 查看 API 日志，确认 Ollama 连接
docker-compose logs -f api

# 测试 API 健康检查
curl http://localhost:8000/api/v1/health
```

## 故障排查

### 问题 1: 容器无法连接到 Ollama

**症状：** API 日志显示 "Connection refused" 或 "Cannot connect to Ollama"

**解决方案：**
```bash
# 1. 确认宿主机 Ollama 正在运行
curl http://localhost:11434/api/tags

# 2. 检查防火墙设置，确保端口 11434 可访问

# 3. 在容器内测试连接
docker-compose exec api curl http://host.docker.internal:11434/api/tags
```

### 问题 2: host.docker.internal 无法解析

**症状：** DNS 解析失败

**解决方案：**
```bash
# 方法 1: 使用宿主机 IP 地址
# 获取宿主机 IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# 修改 docker-compose.yml 中的 OLLAMA_API_URL
# 例如: OLLAMA_API_URL=http://192.168.1.100:11434

# 方法 2: 使用 network_mode: host (仅限 Linux)
# 在 docker-compose.yml 中添加
network_mode: host
```

### 问题 3: Ollama 模型未找到

**症状：** API 返回 "model not found"

**解决方案：**
```bash
# 在宿主机上拉取模型
ollama pull qwen2.5:0.5b

# 验证模型已安装
ollama list
```

## 性能优化

### 1. Ollama 配置

在宿主机上配置 Ollama 环境变量：

```bash
# 设置 GPU 使用（如果有 NVIDIA GPU）
export OLLAMA_GPU_LAYERS=35

# 设置并发请求数
export OLLAMA_NUM_PARALLEL=4

# 设置上下文长度
export OLLAMA_NUM_CTX=4096
```

### 2. Docker 资源限制

在 `docker-compose.yml` 中添加资源限制：

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## 切换回本地 Ollama

如果需要切换回在 Docker 中运行 Ollama：

1. 恢复 `docker-compose.yml` 中的 Ollama 服务定义
2. 修改环境变量：`OLLAMA_API_URL=http://ollama:11434`
3. 添加依赖：`depends_on: ollama`
4. 重新启动服务：`docker-compose up -d --build`

## 推荐配置

对于开发环境，推荐使用远程 Ollama：
- ✅ 节省磁盘空间
- ✅ 更快的启动时间
- ✅ 更容易调试

对于生产环境，推荐使用容器化 Ollama：
- ✅ 完全隔离
- ✅ 更好的可移植性
- ✅ 统一的部署流程
