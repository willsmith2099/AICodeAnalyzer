# Java Ollama Code Analyzer

[简体中文](README.md) | [English](README_EN.md)

这是一个基于 Python 的工具，利用本地运行的 Ollama 大模型 (qwen2.5:0.5b) 来分析 Java 代码。它可以递归扫描指定目录，识别代码功能、潜在 Bug 和改进建议。

## 项目结构 (Project Structure)

项目已重构为模块化结构，以支持更好的扩展性：

```text
coderchange/
├── README.md              # 项目文档
├── requirements.txt       # Python 依赖
├── Dockerfile             # Docker 镜像定义 (新增) 🐳
├── docker-compose.yml     # Docker Compose 配置 (新增) 🐳
├── .dockerignore          # Docker 忽略文件 (新增) 🐳
├── deploy.sh              # 部署脚本 (新增) 🐳
├── DOCKER_DEPLOY.md       # Docker 部署文档 (新增) 🐳
├── src/                   # 源代码目录
│   ├── analyze_java.py    # 基础代码分析工具
│   ├── analyze_impact.py  # 变动影响分析工具
│   ├── llm/               # LLM 客户端模块
│   │   ├── __init__.py
│   │   ├── ollama_client.py    # Ollama API 封装
│   │   └── git_analyzer.py     # Git 变动分析
│   └── prompts/           # 提示词模板模块
│       ├── __init__.py
│       ├── java_analysis.py      # 代码分析提示词
│       ├── impact_analysis.py    # 影响分析提示词
│       └── knowledge_graph.py    # 知识图谱提取提示词
├── web/                   # Web 界面 ⭐
│   ├── app.py             # Flask Web 应用
│   ├── templates/         # HTML 模板
│   │   └── index.html
│   └── static/            # 静态资源
│       ├── css/style.css
│       └── js/app.js
├── api/                   # REST API ⭐
│   ├── server.py          # API 服务器
│   ├── API_DOCS.md        # API 文档
│   └── test_api.py        # API 测试脚本
├── examples/              # 示例代码
│   └── Test.java          # 测试用例
├── analysis_results/      # 基础分析结果（自动生成）
├── impact_reports/        # 影响分析报告（自动生成）
├── web_reports/           # Web 界面报告（自动生成）
└── api_reports/           # API 报告（自动生成）
```

## 功能特性

-   **REST API** 🚀⭐: 完整的 RESTful API 接口，支持程序化调用。
-   **Web 界面** 🌐⭐: 现代化的 Web 界面，支持在线代码分析和报告浏览。
-   **代码分析**: 自动分析 Java、Python、JavaScript 等代码的功能、Bug 和改进点。
-   **变动影响分析** ⭐: 基于 Git 历史分析代码变动的影响范围。
-   **质量报告生成** ⭐: 自动生成包含质量评分、风险评估的专业报告。
-   **模块化设计**: LLM 调用与提示词分离，易于扩展。
-   **知识图谱支持**: 内置知识图谱提取提示词模板 (可扩展)。
-   **结果输出**: 支持将分析结果保存到指定目录的 Markdown 文件。
-   **批量处理**: 递归扫描目录下所有代码文件。


## 使用说明

### 部署方式

#### 方式一：Docker 部署 🐳 (推荐)

**快速启动**:
```bash
# 使用部署脚本（推荐）
./deploy.sh start

# 或使用 docker-compose
docker-compose up -d
```

**拉取 Ollama 模型**:
```bash
docker-compose exec ollama ollama pull qwen2.5:0.5b
```

**访问服务**:
- Web 界面: http://localhost:5001
- API 服务: http://localhost:8000

详细部署文档: [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)

#### 方式二：本地安装

### 前置要求
1.  安装 Python 3.12+
2.  安装并运行 [Ollama](https://ollama.com/)
3.  拉取模型: `ollama pull qwen2.5:0.5b`

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行分析

#### 模式一：Web 界面 🌐 (推荐)

启动 Web 服务器：
```bash
python3 web/app.py
```

然后在浏览器中访问: `http://localhost:5001`

**Web 界面功能**:
- 📝 在线代码分析 - 支持 Java, Python, JavaScript 等
- 📊 报告浏览 - 查看所有历史分析报告
- 🔍 仓库扫描 - 扫描 Git 仓库中的代码文件
- 🎨 现代化 UI - 深色主题，响应式设计
- ⚡ 实时状态 - Ollama 连接状态监控

#### 模式二：基础代码分析

##### 1. 仅在控制台显示结果
```bash
python3 src/analyze_java.py examples/
```

##### 2. 保存结果到文件（推荐）
```bash
python3 src/analyze_java.py examples/ analysis_results/
```
这将在 `analysis_results/` 目录下为每个 Java 文件生成对应的 `*_analysis.md` 文件。

##### 3. 分析任意 Java 工程
```bash
python3 src/analyze_java.py /path/to/your/java/project /path/to/output/directory
```

#### 模式二：变动影响分析 + 质量报告 ⭐

**前提条件**: 项目必须是 Git 仓库

##### 1. 分析当前仓库
```bash
python3 src/analyze_impact.py . impact_reports/
```

##### 2. 分析指定 Git 仓库
```bash
python3 src/analyze_impact.py /path/to/git/repo /path/to/reports
```

**生成的报告包括**:
- `*_analysis.md` - 代码分析报告
- `*_impact.md` - 变动影响分析报告
- `quality_reports/*_quality_report.md` - 综合质量报告

**质量报告内容**:
- 质量评分 (1-10)
- 代码复杂度和可维护性指标
- 关键问题和警告
- 变动影响评估
- 测试建议
- 行动项清单


## 示例输出

运行分析后，会在指定的输出目录生成如下文件：
- `Test_analysis.md` - 包含对 `Test.java` 的完整分析报告

### 分析报告示例

每个分析报告包含：
1. **功能总结** - 代码的主要功能描述
2. **潜在问题** - 发现的 Bug 和安全隐患
3. **改进建议** - 代码优化和重构建议

## REST API 使用

### 启动 API 服务器

```bash
python3 api/server.py
```

API 服务器将在 `http://localhost:8000` 启动。

### API 端点

- `GET  /api/v1/health` - 健康检查
- `GET  /api/v1/status` - 状态信息
- `POST /api/v1/analyze` - 分析代码片段
- `POST /api/v1/analyze/file` - 分析文件
- `POST /api/v1/analyze/repo` - 分析仓库
- `POST /api/v1/impact` - 影响分析
- `GET  /api/v1/reports` - 报告列表
- `GET  /api/v1/reports/<id>` - 获取报告
- `DEL  /api/v1/reports/<id>` - 删除报告

### API 使用示例

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 分析代码
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "public class Test {...}", "language": "java", "save": true}'

# 获取报告列表
curl http://localhost:8000/api/v1/reports?limit=10
```

详细 API 文档请查看: [API_DOCS.md](api/API_DOCS.md)

### API 测试

```bash
python3 api/test_api.py
```

## 扩展开发

### 添加新的提示词模板

在 `src/prompts/` 目录下创建新的 Python 文件，例如：

```python
# src/prompts/custom_analysis.py
def get_custom_prompt(content):
    return f"""
    Your custom prompt here...
    {content}
    """
```

### 使用不同的 LLM 模型

修改 `src/llm/ollama_client.py` 中的 `model` 参数：

```python
client = OllamaClient(model="qwen2.5:7b")  # 使用更大的模型
```

## 技术栈

- **Python 3.12+**
- **Ollama** - 本地 LLM 运行环境
- **qwen2.5:0.5b** - 轻量级大语言模型
- **requests** - HTTP 客户端库
- **GitPython** - Git 仓库操作库
- **Flask** - Web 框架
- **Flask-CORS** - CORS 支持
- **Markdown** - Markdown 渲染库

## 开发计划

- [x] 基础代码分析功能
- [x] 模块化架构重构
- [x] 文件输出功能
- [x] 知识图谱提示词模板
- [x] Git 变动分析集成
- [x] 影响分析功能
- [x] 代码质量报告生成
- [x] Web 界面展示
- [x] 支持多种编程语言（Java, Python, JavaScript 等）
- [x] REST API 接口开发
- [x] Docker 容器化部署
- [ ] 集成 CI/CD 流程
- [ ] 认证和授权系统
- [ ] 性能监控和日志系统

## 许可证

MIT License
