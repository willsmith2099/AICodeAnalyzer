# LangChain 智能代理 - 快速开始

## 5 分钟快速上手

### 步骤 1: 安装依赖

```bash
cd /Users/mac/Desktop/工作/project/coderchange
pip install langchain langchain-community langchain-core
```

### 步骤 2: 确保 Ollama 运行

```bash
# 检查 Ollama 状态
curl http://localhost:11434/api/version

# 如果未运行，启动 Ollama
ollama serve
```

### 步骤 3: 运行示例

```bash
# 运行智能代理演示
python3 examples/langchain_agent_demo.py
```

## 使用场景

### 场景 1: 快速代码审查

```bash
# 使用智能代理分析项目
python3 src/intelligent_scanner.py /path/to/project -o agent_reports -e .java
```

### 场景 2: API 调用

```python
from src.agent.langchain_agent import CodeAnalysisAgent

# 创建代理
agent = CodeAnalysisAgent()

# 分析代码
code = """
public void processData(String input) {
    String query = "SELECT * FROM users WHERE name = '" + input + "'";
    db.execute(query);
}
"""

result = agent.plan_and_execute(
    objective="检查这段代码的安全问题",
    context={"language": "Java", "code": code}
)

print(result)
```

### 场景 3: 自定义分析任务

```python
# 自定义分析
result = agent.analyze(
    task="这段代码的性能如何？有什么优化建议？",
    code=your_code
)
```

## 输出示例

```
================================================================================
示例 1: 基本代码分析
================================================================================

分析结果:
{
  "status": "success",
  "task": "请分析这段代码的安全问题和潜在 bug",
  "result": "发现以下问题:\n1. 使用 eval() 存在严重安全风险...",
  "intermediate_steps": [...]
}
```

## 下一步

- 📖 阅读完整指南: [LANGCHAIN_AGENT_GUIDE.md](LANGCHAIN_AGENT_GUIDE.md)
- 🔧 查看更多示例: [examples/langchain_agent_demo.py](examples/langchain_agent_demo.py)
- 📊 了解架构设计: [LANGCHAIN_INTEGRATION_SUMMARY.md](LANGCHAIN_INTEGRATION_SUMMARY.md)

## 常见问题

**Q: 智能代理和基础扫描器有什么区别？**  
A: 智能代理使用多个专业工具协同分析，提供更深入的见解，但速度较慢。

**Q: 如何禁用智能代理？**  
A: 使用 `--no-agent` 参数：`python3 src/intelligent_scanner.py /path --no-agent`

**Q: 支持哪些编程语言？**  
A: Python, Java, JavaScript, TypeScript, C/C++, Go, Rust 等 20+ 种语言。

---

**开始使用智能代理进行深度代码分析！** 🚀
