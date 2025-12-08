# Directory Scanner 使用示例

本目录包含 Directory Scanner 的各种使用示例。

## 📁 文件说明

### 1. `directory_scanner_examples.sh`
**命令行使用示例脚本**

展示了 10 个常用场景的命令行用法：
- 基本用法
- 远程 Ollama 配置
- 正则表达式过滤
- 调用链分析
- 完整功能组合
- Python 项目分析
- 测试文件分析
- 特定目录分析
- 文件大小限制
- 忽略特定目录

**使用方法**:
```bash
# 查看所有示例
bash examples/directory_scanner_examples.sh

# 或直接执行
chmod +x examples/directory_scanner_examples.sh
./examples/directory_scanner_examples.sh
```

### 2. `directory_scanner_api_demo.py`
**Python API 使用示例**

展示了如何在 Python 代码中使用 Directory Scanner：
- 基本用法
- 远程 Ollama 配置
- 正则表达式过滤
- 调用链分析
- 完整功能组合
- 批量分析
- 自定义分析流程
- 错误处理

**使用方法**:
```bash
python examples/directory_scanner_api_demo.py
```

### 3. `langchain_agent_demo.py`
**LangChain 智能代理示例**

展示如何使用 LangChain 智能代理进行代码分析。

### 4. `incremental_analyzer_demo.py`
**增量分析示例**

展示如何使用增量分析功能。

### 5. `knowledge_graph_demo.py`
**知识图谱示例**

展示如何构建代码知识图谱。

## 🚀 快速开始

### 命令行快速示例

```bash
# 1. 分析当前目录的 Java 文件
python src/directory_scanner.py . -e .java -o reports

# 2. 启用调用链分析
python src/directory_scanner.py . --enable-call-chain -e .java -o reports

# 3. 使用正则过滤
python src/directory_scanner.py . --file-pattern ".*Service.*" -e .java -o reports

# 4. 完整功能
python src/directory_scanner.py /path/to/project \
  --ollama-url http://localhost:11434 \
  --model qwen2.5:0.5b \
  --file-pattern ".*Service.*" \
  --enable-call-chain \
  -e .java \
  -o reports
```

### Python API 快速示例

```python
from src.directory_scanner import DirectoryScanner

# 基本用法
scanner = DirectoryScanner(
    root_dir="./examples",
    output_dir="./reports",
    extensions=['.java']
)
results = scanner.analyze_all()

# 启用调用链分析
scanner = DirectoryScanner(
    root_dir="./examples",
    output_dir="./reports",
    extensions=['.java'],
    enable_call_chain=True
)
results = scanner.analyze_all()
```

## 📊 示例场景

### 场景 1: 分析 Service 层代码

```bash
python src/directory_scanner.py \
  "/path/to/backend/src/main/java/com/example/service/impl" \
  --file-pattern ".*Service.*" \
  --enable-call-chain \
  -e .java \
  -o service_reports
```

### 场景 2: 分析测试代码

```bash
python src/directory_scanner.py ./tests \
  --file-pattern ".*test.*" \
  --enable-call-chain \
  -e .py .java \
  -o test_reports
```

### 场景 3: 使用远程 Ollama

```bash
python src/directory_scanner.py /path/to/project \
  --ollama-url http://192.168.1.100:11434 \
  --model qwen2.5:7b \
  -e .java \
  -o remote_reports
```

### 场景 4: 分析特定模块

```bash
python src/directory_scanner.py /path/to/project \
  --dir-pattern ".*backend.*" \
  --file-pattern ".*Controller.*" \
  --enable-call-chain \
  -e .java \
  -o controller_reports
```

## 🔍 高级用法

### 组合多个过滤条件

```bash
python src/directory_scanner.py /path/to/project \
  --dir-pattern "^(src|lib)$" \
  --file-pattern ".*(Service|Controller|Repository).*" \
  --ignore-dirs test build \
  --max-size 1048576 \
  --enable-call-chain \
  -e .java \
  -o advanced_reports
```

### 批量分析多个项目

```bash
#!/bin/bash
projects=(
  "/path/to/project1"
  "/path/to/project2"
  "/path/to/project3"
)

for project in "${projects[@]}"; do
  echo "分析: $project"
  python src/directory_scanner.py "$project" \
    --enable-call-chain \
    -e .java \
    -o "reports/$(basename $project)"
done
```

## 📚 相关文档

- [调用链分析使用指南](../docs/guides/CALL_CHAIN_ANALYSIS_GUIDE.md)
- [Directory Scanner 高级使用指南](../docs/guides/DIRECTORY_SCANNER_ADVANCED.md)
- [改进总结](../IMPROVEMENT_SUMMARY.md)
- [更新日志](../CHANGELOG_DIRECTORY_SCANNER.md)

## 💡 提示

1. **先测试后批量**: 先在小范围测试，确认配置正确
2. **使用正则过滤**: 减少不必要的文件分析
3. **启用调用链**: 获得更深入的代码分析
4. **保存报告**: 使用 `-o` 参数保存分析结果
5. **查看帮助**: `python src/directory_scanner.py --help`

## 🐛 故障排查

### 问题 1: 找不到模块

```bash
# 确保在项目根目录运行
cd /path/to/coderchange
python src/directory_scanner.py ...
```

### 问题 2: Ollama 连接失败

```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 或使用远程地址
python src/directory_scanner.py . --ollama-url http://remote:11434 ...
```

### 问题 3: 正则表达式不匹配

```bash
# 测试正则表达式
python -c "import re; print(re.search('.*Service.*', 'UserService.java'))"
```

## 🎯 最佳实践

1. 使用有意义的输出目录名
2. 定期清理旧报告
3. 保存重要的分析结果
4. 使用版本控制跟踪配置变化
5. 在 CI/CD 中集成自动分析
