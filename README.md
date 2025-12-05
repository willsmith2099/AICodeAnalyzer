# Java Ollama Code Analyzer

这是一个基于 Python 的工具，利用本地运行的 Ollama 大模型 (qwen2.5:0.5b) 来分析 Java 代码。它可以递归扫描指定目录，识别代码功能、潜在 Bug 和改进建议。

## 项目结构 (Project Structure)

项目已重构为模块化结构，以支持更好的扩展性：

```text
coderchange/
├── README.md              # 项目文档
├── requirements.txt       # Python 依赖
├── src/                   # 源代码目录
│   ├── analyze_java.py    # 主程序入口
│   ├── llm/               # LLM 客户端模块
│   │   ├── __init__.py
│   │   └── ollama_client.py    # Ollama API 封装
│   └── prompts/           # 提示词模板模块
│       ├── __init__.py
│       ├── java_analysis.py    # 代码分析提示词
│       └── knowledge_graph.py  # 知识图谱提取提示词
├── examples/              # 示例代码
│   └── Test.java          # 测试用例
└── analysis_results/      # 分析结果输出目录（自动生成）
    └── Test_analysis.md   # 分析报告示例
```

## 功能特性

-   **代码分析**: 自动分析 Java 代码的功能、Bug 和改进点。
-   **模块化设计**: LLM 调用与提示词分离，易于扩展。
-   **知识图谱支持**: 内置知识图谱提取提示词模板 (可扩展)。
-   **结果输出**: 支持将分析结果保存到指定目录的 Markdown 文件。
-   **批量处理**: 递归扫描目录下所有 Java 文件。

## 使用说明

### 前置要求
1.  安装 Python 3.12+
2.  安装并运行 [Ollama](https://ollama.com/)
3.  拉取模型: `ollama pull qwen2.5:0.5b`

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行分析

#### 1. 仅在控制台显示结果
```bash
python3 src/analyze_java.py examples/
```

#### 2. 保存结果到文件（推荐）
```bash
python3 src/analyze_java.py examples/ analysis_results/
```
这将在 `analysis_results/` 目录下为每个 Java 文件生成对应的 `*_analysis.md` 文件。

#### 3. 分析任意 Java 工程
```bash
python3 src/analyze_java.py /path/to/your/java/project /path/to/output/directory
```

## 示例输出

运行分析后，会在指定的输出目录生成如下文件：
- `Test_analysis.md` - 包含对 `Test.java` 的完整分析报告

### 分析报告示例

每个分析报告包含：
1. **功能总结** - 代码的主要功能描述
2. **潜在问题** - 发现的 Bug 和安全隐患
3. **改进建议** - 代码优化和重构建议

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

## 开发计划

- [x] 基础代码分析功能
- [x] 模块化架构重构
- [x] 文件输出功能
- [x] 知识图谱提示词模板
- [ ] 支持更多编程语言（Python, JavaScript 等）
- [ ] 生成代码质量报告
- [ ] 集成 CI/CD 流程

## 许可证

MIT License
