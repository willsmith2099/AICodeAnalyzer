# Directory Scanner 使用指南

## 概述

Directory Scanner 是一个强大的代码分析工具，支持递归扫描目录并使用 Ollama 进行智能分析。

## 新增功能

### 1. 远程 Ollama 配置

现在支持配置远程 Ollama 服务地址和模型：

```bash
# 使用远程 Ollama 服务
python src/directory_scanner.py /path/to/project --ollama-url http://192.168.1.100:11434

# 使用不同的模型
python src/directory_scanner.py /path/to/project --model qwen2.5:7b

# 组合使用
python src/directory_scanner.py /path/to/project \
  --ollama-url http://192.168.1.100:11434 \
  --model qwen2.5:7b \
  -o reports
```

### 2. 正则表达式过滤

支持使用正则表达式过滤目录和文件：

```bash
# 只分析包含 "test" 的文件
python src/directory_scanner.py /path/to/project --file-pattern ".*test.*"

# 只分析以 "Service" 结尾的文件
python src/directory_scanner.py /path/to/project --file-pattern ".*Service\.py$"

# 只扫描 src 和 lib 目录
python src/directory_scanner.py /path/to/project --dir-pattern "^(src|lib)$"

# 排除 test 目录（使用负向预查）
python src/directory_scanner.py /path/to/project --dir-pattern "^(?!test).*$"
```

## 命令行参数

### 基本参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `directory` | 要扫描的目录路径（必需） | `/path/to/project` |
| `-o, --output` | 分析报告输出目录 | `-o reports` |
| `-e, --extensions` | 要扫描的文件扩展名 | `-e .py .java .js` |
| `--max-size` | 最大文件大小（字节） | `--max-size 2097152` |
| `--ignore-dirs` | 要忽略的目录名称 | `--ignore-dirs test build` |

### Ollama 配置参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--ollama-url` | Ollama 服务地址 | `http://localhost:11434` |
| `--model` | 使用的模型名称 | `qwen2.5:0.5b` |

### 正则表达式过滤参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--dir-pattern` | 目录名正则表达式 | `--dir-pattern "^src$"` |
| `--file-pattern` | 文件名正则表达式 | `--file-pattern ".*Service.*"` |

## 使用示例

### 示例 1: 基本用法

```bash
# 扫描当前目录，保存报告到 reports 目录
python src/directory_scanner.py . -o reports
```

### 示例 2: 使用远程 Ollama

```bash
# 连接到远程 Ollama 服务器
python src/directory_scanner.py /path/to/project \
  --ollama-url http://192.168.1.100:11434 \
  --model qwen2.5:7b \
  -o reports
```

### 示例 3: 只分析 Python 和 Java 文件

```bash
python src/directory_scanner.py /path/to/project \
  -e .py .java \
  -o reports
```

### 示例 4: 使用正则表达式过滤

```bash
# 只分析包含 "Controller" 或 "Service" 的文件
python src/directory_scanner.py /path/to/project \
  --file-pattern ".*(Controller|Service).*" \
  -o reports

# 只扫描 src 目录下的文件
python src/directory_scanner.py /path/to/project \
  --dir-pattern "^src$" \
  -o reports
```

### 示例 5: 组合使用所有功能

```bash
# 完整示例：远程 Ollama + 特定文件类型 + 正则过滤
python src/directory_scanner.py /path/to/project \
  --ollama-url http://192.168.1.100:11434 \
  --model qwen2.5:7b \
  -e .py .java \
  --file-pattern ".*Service.*" \
  --dir-pattern "^(src|lib)$" \
  --max-size 2097152 \
  -o reports
```

### 示例 6: 分析测试文件

```bash
# 只分析测试文件
python src/directory_scanner.py /path/to/project \
  --file-pattern ".*test.*\.py$" \
  -o test_reports
```

### 示例 7: 分析特定模块

```bash
# 只分析 backend 模块中的 Java 文件
python src/directory_scanner.py /path/to/project \
  --dir-pattern ".*backend.*" \
  -e .java \
  -o backend_reports
```

## 正则表达式技巧

### 常用模式

```bash
# 匹配特定前缀
--file-pattern "^test.*"

# 匹配特定后缀
--file-pattern ".*Service\.py$"

# 匹配包含特定字符串
--file-pattern ".*controller.*"

# 匹配多个模式（OR）
--file-pattern ".*(Service|Controller|Repository).*"

# 匹配特定目录
--dir-pattern "^(src|lib|app)$"

# 排除特定模式（使用负向预查）
--file-pattern "^(?!test).*"
```

### 高级示例

```bash
# 只分析以大写字母开头的 Python 文件
python src/directory_scanner.py . --file-pattern "^[A-Z].*\.py$"

# 只分析包含数字的文件
python src/directory_scanner.py . --file-pattern ".*\d+.*"

# 只扫描深度为 1 的目录（需要配合其他工具）
python src/directory_scanner.py . --dir-pattern "^[^/]*$"
```

## 配置远程 Ollama

### 方法 1: 使用命令行参数

```bash
python src/directory_scanner.py /path/to/project \
  --ollama-url http://remote-server:11434 \
  --model qwen2.5:7b
```

### 方法 2: 使用环境变量

```bash
export OLLAMA_URL="http://remote-server:11434"
export OLLAMA_MODEL="qwen2.5:7b"

python src/directory_scanner.py /path/to/project
```

### 方法 3: 在代码中配置

```python
from src.directory_scanner import DirectoryScanner

scanner = DirectoryScanner(
    root_dir="/path/to/project",
    output_dir="reports",
    ollama_url="http://remote-server:11434",
    model="qwen2.5:7b"
)
scanner.analyze_all()
```

## 输出说明

### 控制台输出

```
🤖 Ollama 配置:
   服务地址: http://localhost:11434
   模型名称: qwen2.5:0.5b

🔍 开始扫描目录: /path/to/project
📝 支持的文件类型: .py, .java, .js
📄 文件过滤规则: .*Service.*

✓ 扫描完成，找到 5 个文件
  总大小: 125.50 KB

进度: [1/5]
================================================================================
📄 分析文件: src/UserService.py
🔤 语言: Python
================================================================================
...
```

### 报告文件

- `{filename}_analysis_{timestamp}.md` - 单个文件的分析报告
- `summary_{timestamp}.md` - 汇总报告（Markdown 格式）
- `summary_{timestamp}.json` - 汇总报告（JSON 格式）

## 故障排查

### 问题 1: 无法连接到远程 Ollama

**解决方案：**

1. 检查 Ollama 服务是否运行：
   ```bash
   curl http://remote-server:11434/api/tags
   ```

2. 检查防火墙设置

3. 确认网络连接正常

### 问题 2: 正则表达式不匹配

**解决方案：**

1. 测试正则表达式：
   ```python
   import re
   pattern = re.compile(".*Service.*")
   print(pattern.search("UserService.py"))  # 应该有匹配
   ```

2. 使用更宽松的模式进行测试

3. 检查大小写敏感性

### 问题 3: 模型不存在

**解决方案：**

在 Ollama 服务器上拉取模型：

```bash
# 本地
ollama pull qwen2.5:7b

# 远程（通过 SSH）
ssh user@remote-server "ollama pull qwen2.5:7b"

# Docker
docker exec ollama ollama pull qwen2.5:7b
```

## 性能优化建议

1. **使用正则表达式过滤** - 减少需要分析的文件数量
2. **限制文件大小** - 使用 `--max-size` 跳过大文件
3. **选择合适的模型** - 小模型速度快，大模型质量高
4. **使用本地 Ollama** - 避免网络延迟

## 最佳实践

1. **先测试后批量** - 先在小范围测试，确认配置正确
2. **保存报告** - 使用 `-o` 参数保存分析结果
3. **合理使用过滤** - 只分析需要的文件，提高效率
4. **定期清理** - 定期清理旧的报告文件

## 参考

- [Ollama 官方文档](https://ollama.com/)
- [Python 正则表达式文档](https://docs.python.org/3/library/re.html)
- [项目 README](../README.md)
