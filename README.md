# AI Code Analyzer

[简体中文](README.md) | [English](README_EN.md)

这是一个基于 Python 和 **LangChain** 的智能代码分析工具，利用本地运行的 Ollama 大模型 (qwen2.5:0.5b) 来分析代码。它集成了 **LangChain 智能代理框架**，基于 ReAct (Reasoning + Acting) 架构，能够自主规划分析任务、选择合适的工具，并提供深度的代码质量分析、安全审查和改进建议。

### 核心特性

- 🤖 **LangChain 智能代理** - 基于 ReAct 框架的自主规划和工具调用
- 🔍 **智能目录扫描** - 递归扫描并批量分析多种编程语言
- 📊 **Neo4j 知识图谱** - 将代码结构存储为可查询的图数据库
- 🌐 **Web 界面** - 现代化的在线代码分析平台
- 🚀 **REST API** - 完整的 RESTful API 接口
- 🐳 **Docker 部署** - 一键容器化部署

## 项目结构 (Project Structure)

项目已重构为模块化结构，以支持更好的扩展性：


```text
AICodeAnalyzer/ 
├── README.md              # 项目文档
├── README_EN.md           # 英文文档
├── requirements.txt       # Python 依赖
├── docs/                  # 文档目录 📚
│   ├── README.md          # 文档索引
│   ├── guides/            # 使用指南
│   │   ├── DIRECTORY_SCANNER_GUIDE.md  # 目录扫描器指南
│   │   ├── LANGCHAIN_AGENT_GUIDE.md    # LangChain 智能代理指南
│   │   ├── AGENT_VERIFICATION_GUIDE.md # 智能代理验证指南
│   │   ├── QUICKSTART_LANGCHAIN.md     # LangChain 快速开始
│   │   ├── DOCKER_DEPLOY.md            # Docker 部署指南
│   │   └── NEO4J_GUIDE.md              # Neo4j 使用指南
│   └── reports/           # 项目报告
│       ├── PROJECT_SUMMARY.md          # 项目总结
│       ├── GIT_COMMIT_SUMMARY.md       # Git 提交总结
│       ├── LANGCHAIN_INTEGRATION_SUMMARY.md  # LangChain 集成总结
│       ├── LANGCHAIN_COMPLETION_REPORT.md    # LangChain 完成报告
│       └── AGENT_VERIFICATION_SUMMARY.md     # 智能代理验证总结
├── docker/                # Docker 配置 🐳
│   ├── README.md          # Docker 文档
│   ├── Dockerfile         # Docker 镜像定义
│   ├── docker-compose.yml # 服务编排配置
│   └── deploy.sh          # 部署脚本
├── src/                   # 源代码目录
│   ├── analyze_java.py    # 基础代码分析工具
│   ├── analyze_impact.py  # 变动影响分析工具
│   ├── directory_scanner.py  # 目录扫描器
│   ├── intelligent_scanner.py  # 智能目录扫描器 🤖⭐
│   ├── agent/             # LangChain 智能代理模块 🤖⭐
│   │   ├── __init__.py
│   │   └── langchain_agent.py   # 智能代码分析代理
│   ├── llm/               # LLM 客户端模块
│   │   ├── __init__.py
│   │   ├── ollama_client.py    # Ollama API 封装
│   │   └── git_analyzer.py     # Git 变动分析
│   ├── prompts/           # 提示词模板模块
│   │   ├── __init__.py
│   │   ├── java_analysis.py      # 代码分析提示词
│   │   ├── impact_analysis.py    # 影响分析提示词
│   │   └── knowledge_graph.py    # 知识图谱提取提示词
│   └── graph/             # 图数据库模块 📊⭐
│       ├── __init__.py
│       ├── neo4j_client.py       # Neo4j 客户端
│       └── code_parser.py        # 代码解析器
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
├── tests/                 # 测试目录 🧪
│   ├── README.md          # 测试文档
│   ├── TEST_REPORT.md     # 测试报告
│   ├── PYTHON312_TEST_REPORT.md  # Python 3.12 测试报告
│   └── graph/             # 图数据库测试
│       ├── README.md      # 图测试文档
│       ├── test_neo4j.py  # Neo4j 测试脚本
│       └── graph_example.py  # 图数据库示例
├── examples/              # 示例代码
│   ├── Test.java          # 简单测试用例
│   ├── Application.java   # 复杂测试用例
│   └── langchain_agent_demo.py  # LangChain 智能代理示例 🤖⭐
├── analysis_results/      # 基础分析结果（自动生成）
├── impact_reports/        # 影响分析报告（自动生成）
├── web_reports/           # Web 界面报告（自动生成）
└── api_reports/           # API 报告（自动生成）
```


## 功能特性


-   **REST API** 🚀⭐: 完整的 RESTful API 接口，支持程序化调用。
-   **Web 界面** 🌐⭐: 现代化的 Web 界面，支持在线代码分析和报告浏览。
-   **Neo4j 图数据库** 📊⭐: 将代码结构存储为知识图谱，支持复杂查询和可视化。
-   **LangChain 智能代理** 🤖⭐: 基于 ReAct 框架的智能代码分析代理，支持自主规划和工具调用。
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
cd docker
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
- Neo4j 浏览器: http://localhost:7474 (用户名: neo4j, 密码: password)

详细部署文档: [DOCKER_DEPLOY.md](docs/guides/DOCKER_DEPLOY.md)
Neo4j 使用指南: [NEO4J_GUIDE.md](docs/guides/NEO4J_GUIDE.md)
Docker 配置说明: [docker/README.md](docker/README.md)



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

#### 模式三：LangChain 智能代理 🤖⭐

**功能**: 使用 LangChain 框架实现智能规划和工具调用的深度代码分析

##### 1. 安装依赖
```bash
pip install langchain langchain-community langchain-core
```

##### 2. 使用智能扫描器
```bash
# 使用智能代理进行深度分析
python3 src/intelligent_scanner.py /path/to/project -o agent_reports -e .java

# 禁用智能代理，使用基础模式
python3 src/intelligent_scanner.py /path/to/project -o reports --no-agent
```

##### 3. 直接使用智能代理 API
```python
from src.agent.langchain_agent import CodeAnalysisAgent

# 创建智能代理
agent = CodeAnalysisAgent()

# 方法 1: 简单分析
result = agent.analyze(
    task="请分析这段代码的质量和潜在问题",
    code=your_code
)

# 方法 2: 规划和执行
result = agent.plan_and_execute(
    objective="对这段代码进行完整的代码审查",
    context={"language": "Java", "code": your_code}
)
```

##### 4. 运行示例
```bash
python3 examples/langchain_agent_demo.py
```

**智能代理工具集**:
- 🔍 代码质量分析 - 结构、命名、注释
- 🐛 Bug 检测 - 逻辑错误、空指针风险
- 💡 改进建议 - 重构、性能优化
- 🔒 安全分析 - SQL 注入、XSS 漏洞
- 📦 依赖提取 - 导入库和模块
- 📊 复杂度计算 - 圈复杂度、代码行数
- 📝 代码摘要 - 功能描述生成

**工作原理**:
- 基于 ReAct (Reasoning + Acting) 框架
- 智能代理自主选择工具和执行顺序
- 支持多轮推理和工具调用
- 生成详细的分析计划和执行报告

详细使用指南: [LANGCHAIN_AGENT_GUIDE.md](docs/guides/LANGCHAIN_AGENT_GUIDE.md)

#### 模式四：Neo4j 知识图谱 📊⭐

**前提条件**: Neo4j 数据库运行中

##### 1. 启动 Neo4j (Docker)
```bash
cd docker
docker-compose up -d neo4j
```

##### 2. 解析代码到图数据库
```bash
python3.12 tests/graph/graph_example.py examples/
```

##### 3. 查询图数据库
```python
from src.graph.neo4j_client import Neo4jClient

client = Neo4jClient()

# 获取统计信息
stats = client.get_statistics()
print(f"类: {stats['classes']}, 方法: {stats['methods']}")

# 搜索方法
methods = client.search_methods_by_name("process")

# 获取类层次结构
hierarchy = client.get_class_hierarchy("MyClass")
```

**图数据库功能**:
- 🔍 代码结构可视化
- 📊 依赖关系分析
- 🔗 方法调用链追踪
- 📈 继承层次查询
- 🎯 影响范围评估

详细使用指南: [NEO4J_GUIDE.md](docs/guides/NEO4J_GUIDE.md)
测试文档: [tests/graph/README.md](tests/graph/README.md)



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

### 核心技术

- **Python 3.12+** - 主要编程语言
- **Ollama** - 本地 LLM 运行环境
- **qwen2.5:0.5b** - 轻量级大语言模型

### AI 框架

- **LangChain 0.1+** 🤖⭐ - AI 应用开发框架
  - `langchain` - 核心框架
  - `langchain-community` - 社区集成
  - `langchain-core` - 核心抽象
- **ReAct Framework** - 推理与行动框架

### 后端框架

- **Flask** - Web 框架
- **Flask-CORS** - CORS 支持
- **requests** - HTTP 客户端库

### 数据处理

- **GitPython** - Git 仓库操作库
- **Markdown** - Markdown 渲染库
- **Neo4j** - 图数据库


## 开发计划

### 已完成功能 ✅

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
- [x] Neo4j 图数据库集成
- [x] **目录扫描器** 🔍⭐ - 递归扫描和批量分析
- [x] **LangChain 智能代理** 🤖⭐ - 基于 ReAct 框架的智能分析
  - [x] 7 个专业分析工具
  - [x] 自主规划和工具调用
  - [x] 智能目录扫描器集成
  - [x] 完整的使用文档和示例

### 进行中 🚧

- [ ] LangChain 智能代理优化
  - [ ] 添加更多专业工具
  - [ ] 优化提示词模板
  - [ ] 工具调用缓存机制
  - [ ] 并行工具调用支持

### 计划中 📋

#### 短期计划 (1-2 周)

- [ ] 集成 CI/CD 流程
- [ ] 认证和授权系统
- [ ] 性能监控和日志系统
- [ ] 向量数据库集成（代码语义搜索）
- [ ] 智能代理记忆机制

#### 中期计划 (1-2 月)

- [ ] 多模型支持（GPT-4、Claude 等）
- [ ] Web 界面集成智能代理
- [ ] 增量代码分析
- [ ] 代码知识图谱构建
- [ ] 自动化测试覆盖率分析

#### 长期计划 (3-6 月)

- [ ] 自动学习和优化工具选择策略
- [ ] 跨项目代码分析和对比
- [ ] 代码生成和自动修复建议
- [ ] 团队协作功能
- [ ] 企业级部署方案


## 许可证

MIT License
