# Docker 部署指南

## 快速开始

### 使用 Docker Compose（推荐）

1. **启动所有服务**
```bash
docker-compose up -d
```

这将启动三个容器：
- `code-analyzer-ollama` - Ollama LLM 服务 (端口 11434)
- `code-analyzer-api` - REST API 服务 (端口 8000)
- `code-analyzer-web` - Web 界面 (端口 5001)

2. **拉取 Ollama 模型**
```bash
docker-compose exec ollama ollama pull qwen2.5:0.5b
```

3. **访问服务**
- Web 界面: http://localhost:5001
- API 文档: http://localhost:8000/api/v1/status

4. **查看日志**
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api
docker-compose logs -f web
docker-compose logs -f ollama
```

5. **停止服务**
```bash
docker-compose down
```

6. **停止并删除数据**
```bash
docker-compose down -v
```

### 使用单独的 Docker 容器

#### 1. 构建镜像
```bash
docker build -t code-analyzer:latest .
```

#### 2. 运行 Ollama（必需）
```bash
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama_data:/root/.ollama \
  ollama/ollama:latest

# 拉取模型
docker exec ollama ollama pull qwen2.5:0.5b
```

#### 3. 运行 API 服务
```bash
docker run -d \
  --name code-analyzer-api \
  -p 8000:8000 \
  --link ollama:ollama \
  -e OLLAMA_API_URL=http://ollama:11434 \
  -v $(pwd)/api_reports:/app/api_reports \
  code-analyzer:latest \
  python3 api/server.py
```

#### 4. 运行 Web 服务
```bash
docker run -d \
  --name code-analyzer-web \
  -p 5001:5001 \
  --link ollama:ollama \
  -e OLLAMA_API_URL=http://ollama:11434 \
  -v $(pwd)/web_reports:/app/web_reports \
  code-analyzer:latest \
  python3 web/app.py
```

## 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `OLLAMA_API_URL` | `http://localhost:11434` | Ollama API 地址 |
| `PYTHONUNBUFFERED` | `1` | Python 输出不缓冲 |

## 数据持久化

### 卷映射

Docker Compose 自动创建以下卷：

- `ollama_data` - Ollama 模型数据
- `./api_reports` - API 生成的报告
- `./web_reports` - Web 生成的报告

### 备份数据

```bash
# 备份 Ollama 模型
docker run --rm -v ollama_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/ollama_backup.tar.gz -C /data .

# 恢复 Ollama 模型
docker run --rm -v ollama_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/ollama_backup.tar.gz -C /data
```

## 健康检查

所有服务都配置了健康检查：

```bash
# 检查服务状态
docker-compose ps

# 手动健康检查
curl http://localhost:8000/api/v1/health
curl http://localhost:5001/health
curl http://localhost:11434/api/tags
```

## 故障排查

### 1. Ollama 连接失败

```bash
# 检查 Ollama 是否运行
docker-compose ps ollama

# 查看 Ollama 日志
docker-compose logs ollama

# 重启 Ollama
docker-compose restart ollama
```

### 2. 模型未找到

```bash
# 进入 Ollama 容器
docker-compose exec ollama bash

# 列出已安装的模型
ollama list

# 拉取模型
ollama pull qwen2.5:0.5b
```

### 3. 端口冲突

修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8001:8000"  # 将 API 端口改为 8001
```

### 4. 权限问题

```bash
# 修复报告目录权限
chmod -R 777 api_reports web_reports
```

## 生产环境部署

### 1. 使用反向代理（Nginx）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:5001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 添加 SSL/TLS

```bash
# 使用 Let's Encrypt
docker run -it --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  certbot/certbot certonly --standalone \
  -d your-domain.com
```

### 3. 资源限制

在 `docker-compose.yml` 中添加：

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### 4. 日志管理

```yaml
services:
  api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 更新和维护

### 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

### 更新 Ollama 模型

```bash
docker-compose exec ollama ollama pull qwen2.5:0.5b
```

### 清理未使用的资源

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的卷
docker volume prune

# 清理所有未使用的资源
docker system prune -a
```

## 监控

### 查看资源使用

```bash
# 实时监控
docker stats

# 查看特定容器
docker stats code-analyzer-api code-analyzer-web
```

### 日志聚合

```bash
# 导出日志
docker-compose logs --no-color > logs.txt

# 实时跟踪
docker-compose logs -f --tail=100
```

## 安全建议

1. **不要在生产环境使用 debug 模式**
2. **使用环境变量管理敏感信息**
3. **定期更新基础镜像**
4. **限制容器资源使用**
5. **使用非 root 用户运行容器**
6. **启用 Docker 内容信任**

## 性能优化

1. **使用多阶段构建减小镜像大小**
2. **优化层缓存**
3. **使用 .dockerignore 排除不必要的文件**
4. **配置合适的健康检查间隔**
5. **使用卷而非绑定挂载提高 I/O 性能**
