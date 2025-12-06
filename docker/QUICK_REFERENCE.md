# 🚀 Docker 部署快速参考

## ✅ 当前状态：运行中

所有服务已成功部署并运行正常！

---

## 🌐 访问地址

| 服务 | URL | 状态 |
|------|-----|------|
| **Web 界面** | http://localhost:5001 | ✅ 健康 |
| **API 服务** | http://localhost:8000 | ✅ 健康 |
| **Neo4j 浏览器** | http://localhost:7474 | ✅ 健康 |

**Neo4j 登录信息**:
- 用户名: `neo4j`
- 密码: `password`

---

## 🎯 常用命令

### 服务管理
```bash
# 进入 docker 目录
cd docker

# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api
docker-compose logs -f web
```

### 健康检查
```bash
# API 健康检查
curl http://localhost:8000/api/v1/health

# Web 健康检查
curl http://localhost:5001/health

# API 状态查询
curl http://localhost:8000/api/v1/status
```

### 代码分析
```bash
# 分析代码片段
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello():\n    print(\"Hello\")",
    "language": "python"
  }'

# 查看所有报告
curl http://localhost:8000/api/v1/reports
```

---

## 🔧 配置信息

### 远程 Ollama
- 宿主机地址: `http://host.docker.internal:11434`
- 模型: `qwen2.5:0.5b`
- 状态: ✅ 已连接

### 环境变量
```yaml
OLLAMA_API_URL: http://host.docker.internal:11434
NEO4J_URI: bolt://neo4j:7687
NEO4J_USER: neo4j
NEO4J_PASSWORD: password
```

---

## 📊 服务状态

```
NAME                  STATUS              PORTS
code-analyzer-api     ✅ healthy          8000:8000
code-analyzer-web     ✅ healthy          5001:5001
code-analyzer-neo4j   ✅ healthy          7474:7474, 7687:7687
```

**健康检查响应**:
```json
{
  "status": "healthy",
  "ollama": "connected",
  "version": "v1"
}
```

---

## 🐛 故障排查

### Ollama 连接问题
```bash
# 1. 检查宿主机 Ollama
curl http://localhost:11434/api/tags

# 2. 检查模型
ollama list

# 3. 从容器内测试
docker-compose exec api curl http://host.docker.internal:11434/api/tags
```

### 服务无法启动
```bash
# 1. 查看日志
docker-compose logs api

# 2. 重新构建
docker-compose up -d --build

# 3. 清理并重启
docker-compose down
docker-compose up -d
```

### 端口冲突
```bash
# 检查端口占用
lsof -i :5001
lsof -i :8000
lsof -i :7474
```

---

## 📚 文档

- **部署指南**: `DOCKER_DEPLOY.md`
- **远程 Ollama 配置**: `REMOTE_OLLAMA_CONFIG.md`
- **测试报告**: `TEST_REPORT.md`
- **测试总结**: `DOCKER_TEST_SUMMARY.md`

---

## 💡 提示

1. **首次使用**: 访问 http://localhost:5001 开始使用 Web 界面
2. **API 文档**: 访问 http://localhost:8000/api/v1/status 查看所有端点
3. **图数据库**: 访问 http://localhost:7474 查看代码关系图
4. **日志监控**: 使用 `docker-compose logs -f` 实时查看日志

---

## 🎉 成功部署！

所有服务已就绪，可以开始使用 AI 代码分析工具了！

**下一步**:
1. 访问 Web 界面进行代码分析
2. 使用 API 集成到您的工作流
3. 查看 Neo4j 中的代码关系图

---

**更新时间**: 2025-12-06 09:18  
**部署方式**: Docker Compose + 远程 Ollama  
**状态**: ✅ 全部正常
