# LangChain 智能代理验证指南

## 验证步骤

由于终端输出环境限制，请按以下步骤手动验证智能代理功能：

### 步骤 1: 验证依赖安装

在您的终端中运行：

```bash
cd /Users/mac/Desktop/工作/project/coderchange

# 检查 LangChain 是否安装
python3 -c "import langchain; print(f'LangChain version: {langchain.__version__}')"

# 检查所有依赖
python3 -c "
import langchain
import langchain_community  
import langchain_core
print('✓ 所有 LangChain 依赖已安装')
"
```

### 步骤 2: 验证 Ollama 服务

```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/version

# 如果未运行，启动 Ollama
ollama serve

# 或使用 Docker
docker-compose up -d ollama
```

### 步骤 3: 测试智能代理导入

```bash
python3 -c "
import sys
sys.path.insert(0, 'src')
from agent.langchain_agent import CodeAnalysisAgent, OllamaLLM
print('✓ 智能代理模块导入成功')
"
```

### 步骤 4: 创建并测试智能代理

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

from agent.langchain_agent import CodeAnalysisAgent

# 创建智能代理
print("创建智能代理...")
agent = CodeAnalysisAgent()

print(f"✓ 智能代理创建成功")
print(f"  工具数量: {len(agent.tools)}")
print(f"  工具列表:")
for tool in agent.tools:
    print(f"    - {tool.name}: {tool.description[:50]}...")

# 测试简单分析
print("\n测试代码分析...")
test_code = """
def calculate(a, b):
    result = a + b
    return result
"""

result = agent.analyze(
    task="请简要分析这段代码的功能",
    code=test_code
)

print(f"\n分析状态: {result['status']}")
if result['status'] == 'success':
    print(f"分析结果:\n{result['result'][:300]}...")
    print("\n✓✓✓ 智能代理测试成功！")
else:
    print(f"分析失败: {result.get('error')}")
EOF
```

### 步骤 5: 运行完整示例

```bash
# 运行智能代理演示
python3 examples/langchain_agent_demo.py
```

### 步骤 6: 使用智能扫描器

```bash
# 分析示例文件
python3 src/intelligent_scanner.py examples/ -o test_agent_reports -e .java

# 查看生成的报告
ls -lh test_agent_reports/
cat test_agent_reports/summary_*.md
```

## 预期输出

### 成功的输出示例

```
创建智能代理...
✓ 智能代理创建成功
  工具数量: 7
  工具列表:
    - analyze_code_quality: 分析代码质量，包括代码结构、命名规范...
    - detect_bugs: 检测代码中的潜在 bug 和逻辑错误...
    - suggest_improvements: 提供代码改进建议，包括重构、性能优化...
    - analyze_security: 分析代码的安全隐患，如 SQL 注入、XSS 等...
    - extract_dependencies: 提取代码的依赖关系和导入的库...
    - calculate_complexity: 计算代码复杂度（圈复杂度、认知复杂度等）...
    - generate_summary: 生成代码功能摘要和文档...

测试代码分析...

分析状态: success
分析结果:
这段代码定义了一个简单的计算函数...
[详细分析内容]

✓✓✓ 智能代理测试成功！
```

## 故障排除

### 问题 1: 导入错误

**错误**: `ModuleNotFoundError: No module named 'langchain'`

**解决方案**:
```bash
pip install langchain langchain-community langchain-core
```

### 问题 2: Ollama 连接失败

**错误**: `Error calling Ollama: Connection refused`

**解决方案**:
```bash
# 启动 Ollama
ollama serve

# 或检查 Docker
docker-compose ps
docker-compose up -d ollama
```

### 问题 3: 工具调用失败

**错误**: `Agent stopped due to max iterations`

**解决方案**:
- 这是正常的，表示代理达到了最大迭代次数
- 可以在创建代理时调整 `max_iterations` 参数

### 问题 4: 分析速度慢

**说明**: 智能代理模式比基础模式慢 3-6 倍是正常的

**优化建议**:
- 使用更大的模型 (qwen2.5:7b)
- 限制文件大小
- 使用 `--no-agent` 参数切换到基础模式

## 验证清单

完成以下检查以确保智能代理正常工作：

- [ ] LangChain 依赖已安装
- [ ] Ollama 服务正在运行
- [ ] 智能代理模块可以导入
- [ ] 智能代理可以成功创建
- [ ] 7 个工具都已注册
- [ ] 简单代码分析可以执行
- [ ] 生成的报告格式正确

## 快速验证命令

一键验证所有功能：

```bash
cd /Users/mac/Desktop/工作/project/coderchange

# 运行验证脚本
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

print("=" * 60)
print("LangChain 智能代理验证")
print("=" * 60)

# 1. 导入测试
print("\n[1/5] 测试模块导入...")
try:
    from agent.langchain_agent import CodeAnalysisAgent
    print("✓ 导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 2. Ollama 测试
print("\n[2/5] 测试 Ollama 连接...")
import requests
try:
    r = requests.get("http://localhost:11434/api/version", timeout=3)
    print(f"✓ Ollama 运行中")
except Exception as e:
    print(f"✗ Ollama 未运行: {e}")
    sys.exit(1)

# 3. 创建代理
print("\n[3/5] 创建智能代理...")
try:
    agent = CodeAnalysisAgent()
    print(f"✓ 代理创建成功 ({len(agent.tools)} 个工具)")
except Exception as e:
    print(f"✗ 创建失败: {e}")
    sys.exit(1)

# 4. 工具验证
print("\n[4/5] 验证工具...")
expected_tools = [
    'analyze_code_quality',
    'detect_bugs',
    'suggest_improvements',
    'analyze_security',
    'extract_dependencies',
    'calculate_complexity',
    'generate_summary'
]
actual_tools = [t.name for t in agent.tools]
for tool_name in expected_tools:
    if tool_name in actual_tools:
        print(f"  ✓ {tool_name}")
    else:
        print(f"  ✗ {tool_name} 缺失")

# 5. 简单分析测试
print("\n[5/5] 测试代码分析...")
try:
    code = "def hello(): return 'world'"
    result = agent.analyze(task="分析这段代码", code=code)
    if result['status'] == 'success':
        print("✓ 分析成功")
    else:
        print(f"✗ 分析失败: {result.get('error')}")
except Exception as e:
    print(f"✗ 分析异常: {e}")

print("\n" + "=" * 60)
print("验证完成！")
print("=" * 60)
EOF
```

## 下一步

验证成功后，您可以：

1. **运行完整示例**: `python3 examples/langchain_agent_demo.py`
2. **分析实际项目**: `python3 src/intelligent_scanner.py /path/to/project -o reports`
3. **阅读详细文档**: [LANGCHAIN_AGENT_GUIDE.md](LANGCHAIN_AGENT_GUIDE.md)

---

**如有问题，请查看**: [LANGCHAIN_AGENT_GUIDE.md](LANGCHAIN_AGENT_GUIDE.md) 的故障排除部分
