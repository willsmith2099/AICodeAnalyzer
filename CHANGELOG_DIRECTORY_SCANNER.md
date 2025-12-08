# Directory Scanner 更新说明

## 新增功能（2025-12-08）

### 1. 远程 Ollama 配置支持

现在可以通过命令行参数配置远程 Ollama 服务地址和模型：

```bash
# 使用远程 Ollama 服务
python src/directory_scanner.py /path/to/project \
  --ollama-url http://192.168.1.100:11434 \
  --model qwen2.5:7b

# 查看帮助
python src/directory_scanner.py --help
```

**新增参数：**
- `--ollama-url`: Ollama 服务地址（默认: http://localhost:11434）
- `--model`: 使用的模型名称（默认: qwen2.5:0.5b）

### 2. 正则表达式过滤支持

支持使用正则表达式过滤目录和文件，实现更精确的扫描控制：

```bash
# 只分析包含 "Service" 的文件
python src/directory_scanner.py /path/to/project \
  --file-pattern ".*Service.*"

# 只扫描 src 和 lib 目录
python src/directory_scanner.py /path/to/project \
  --dir-pattern "^(src|lib)$"

# 组合使用
python src/directory_scanner.py /path/to/project \
  --file-pattern ".*Controller.*" \
  --dir-pattern "^src$"
```

**新增参数：**
- `--dir-pattern`: 目录名正则表达式（只扫描匹配的目录）
- `--file-pattern`: 文件名正则表达式（只分析匹配的文件）

## 使用示例

### 示例 1: 分析远程项目

```bash
# 连接到远程 Ollama 服务器，使用更强大的模型
python src/directory_scanner.py /path/to/project \
  --ollama-url http://192.168.1.100:11434 \
  --model qwen2.5:7b \
  -o reports
```

### 示例 2: 只分析测试文件

```bash
# 使用正则表达式只分析测试文件
python src/directory_scanner.py /path/to/project \
  --file-pattern ".*[Tt]est.*" \
  -e .py .java \
  -o test_reports
```

### 示例 3: 分析特定模块

```bash
# 只分析 backend 模块中的 Service 类
python src/directory_scanner.py /path/to/project \
  --dir-pattern ".*backend.*" \
  --file-pattern ".*Service\.java$" \
  -o backend_service_reports
```

### 示例 4: 完整配置

```bash
# 组合所有功能
python src/directory_scanner.py /path/to/project \
  --ollama-url http://192.168.1.100:11434 \
  --model qwen2.5:7b \
  -e .py .java \
  --file-pattern ".*(Service|Controller|Repository).*" \
  --dir-pattern "^(src|lib)$" \
  --max-size 2097152 \
  -o comprehensive_reports
```

## 测试

运行测试脚本验证新功能：

```bash
python tests/test_directory_scanner.py
```

## 文档

详细使用指南请参考：
- [Directory Scanner 高级使用指南](docs/guides/DIRECTORY_SCANNER_ADVANCED.md)
- [项目 README](README.md)

## 技术细节

### 配置优先级

Ollama 配置的优先级：
1. 命令行参数 `--ollama-url` 和 `--model`
2. 构造函数参数（代码中指定）
3. 默认值

### 正则表达式说明

- **目录过滤** (`--dir-pattern`): 
  - 匹配目录名（不包含路径）
  - 如果设置，只扫描匹配的目录
  - 忽略列表仍然生效

- **文件过滤** (`--file-pattern`):
  - 匹配文件名（不包含路径）
  - 如果设置，只分析匹配的文件
  - 扩展名过滤仍然生效

### 正则表达式示例

```python
# 匹配以大写字母开头的文件
--file-pattern "^[A-Z].*"

# 匹配包含数字的文件
--file-pattern ".*\d+.*"

# 匹配多个模式（OR）
--file-pattern ".*(Service|Controller|Repository).*"

# 精确匹配目录名
--dir-pattern "^(src|lib|app)$"

# 排除特定模式（使用负向预查）
--file-pattern "^(?!test).*"
```

## 向后兼容性

所有新增参数都是可选的，不影响现有用法：

```bash
# 原有用法仍然有效
python src/directory_scanner.py /path/to/project -o reports
python src/directory_scanner.py /path/to/project -e .py .java
```

## 更新日志

### v2.0.0 (2025-12-08)

**新增功能：**
- ✨ 支持远程 Ollama 服务配置
- ✨ 支持自定义模型选择
- ✨ 支持正则表达式过滤目录
- ✨ 支持正则表达式过滤文件

**改进：**
- 📝 增强的命令行帮助信息
- 🧪 新增测试脚本
- 📚 完善的使用文档

**技术债务：**
- 无破坏性更改
- 完全向后兼容
