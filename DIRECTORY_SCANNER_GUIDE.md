# 目录扫描器使用说明

## 功能说明

`directory_scanner.py` 可以递归扫描指定目录下的程序文件，并使用 Ollama 大语言模型进行深度分析。

## 使用方法

### 1. 基本用法

分析 lingtools 项目的所有 Java 文件：

```bash
cd /Users/mac/Desktop/工作/project/coderchange
python3 src/directory_scanner.py /Users/mac/Desktop/cursor/lingtools -o analysis_reports -e .java
```

### 2. 命令参数说明

```
python3 src/directory_scanner.py <目录路径> [选项]

必需参数:
  <目录路径>          要扫描的目录路径

可选参数:
  -o, --output        分析报告输出目录
  -e, --extensions    要扫描的文件扩展名（例如: .py .java .js）
  --max-size          最大文件大小（字节），默认 1MB
  --ignore-dirs       要忽略的目录名称
```

### 3. 使用示例

#### 示例 1: 分析所有 Java 文件
```bash
python3 src/directory_scanner.py /Users/mac/Desktop/cursor/lingtools -o analysis_reports -e .java
```

#### 示例 2: 分析多种文件类型
```bash
python3 src/directory_scanner.py /Users/mac/Desktop/cursor/lingtools -o analysis_reports -e .java .py .js
```

#### 示例 3: 设置文件大小限制
```bash
python3 src/directory_scanner.py /Users/mac/Desktop/cursor/lingtools -o analysis_reports -e .java --max-size 512000
```

#### 示例 4: 忽略特定目录
```bash
python3 src/directory_scanner.py /Users/mac/Desktop/cursor/lingtools -o analysis_reports -e .java --ignore-dirs test docs
```

## 输出说明

### 控制台输出

扫描器会在控制台显示：
- 扫描进度
- 找到的文件列表
- 每个文件的分析结果
- 统计信息

### 生成的报告文件

在指定的输出目录（例如 `analysis_reports/`）中会生成：

1. **单个文件分析报告** (Markdown 格式)
   - 文件名格式: `<文件路径>_analysis_<时间戳>.md`
   - 包含: 代码概述、质量评估、潜在问题、改进建议等

2. **汇总报告** (Markdown 格式)
   - 文件名格式: `summary_<时间戳>.md`
   - 包含: 统计信息、所有文件的分析状态列表

3. **汇总报告** (JSON 格式)
   - 文件名格式: `summary_<时间戳>.json`
   - 包含: 完整的结构化数据，便于程序化处理

## 支持的编程语言

- Python (.py)
- Java (.java)
- JavaScript (.js)
- TypeScript (.ts)
- C/C++ (.c, .cpp, .h, .hpp)
- Go (.go)
- Rust (.rs)
- 以及其他 20+ 种语言

## 前置要求

1. **Ollama 服务运行中**
   ```bash
   # 检查 Ollama 状态
   curl http://localhost:11434/api/version
   
   # 如果未运行，启动 Ollama
   ollama serve
   
   # 或使用 Docker
   docker-compose up -d ollama
   ```

2. **已安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

## 故障排除

### 问题 1: Ollama 连接失败

**错误**: `Error communicating with Ollama`

**解决方案**:
```bash
# 确保 Ollama 正在运行
ollama serve

# 或重启 Docker 服务
docker-compose restart ollama
```

### 问题 2: 找不到模块

**错误**: `ModuleNotFoundError: No module named 'llm'`

**解决方案**:
```bash
# 确保在项目根目录运行
cd /Users/mac/Desktop/工作/project/coderchange
python3 src/directory_scanner.py ...
```

### 问题 3: 权限错误

**错误**: `Permission denied`

**解决方案**:
```bash
# 确保有读取目标目录的权限
ls -la /Users/mac/Desktop/cursor/lingtools

# 确保有写入输出目录的权限
mkdir -p analysis_reports
chmod 755 analysis_reports
```

## 性能建议

1. **限制文件大小**: 使用 `--max-size` 避免分析过大的文件
2. **指定文件类型**: 使用 `-e` 只分析需要的文件类型
3. **忽略无关目录**: 使用 `--ignore-dirs` 跳过测试、文档等目录
4. **分批处理**: 对于大型项目，可以分目录进行分析

## 查看分析报告

```bash
# 查看汇总报告
cat analysis_reports/summary_*.md

# 查看特定文件的分析
ls analysis_reports/
cat analysis_reports/<文件名>_analysis_*.md

# 使用 Markdown 预览器
open analysis_reports/summary_*.md
```

## 示例输出

```
🔍 开始扫描目录: /Users/mac/Desktop/cursor/lingtools
📝 支持的文件类型: .java

✓ 扫描完成，找到 15 个文件
  总大小: 234.56 KB

进度: [1/15]
================================================================================
📄 分析文件: backend/src/main/java/com/example/Application.java
🔤 语言: Java
================================================================================

🤖 正在调用 Ollama 进行分析...

================================================================================
📊 分析结果
================================================================================
[分析内容...]

✓ 分析报告已保存: analysis_reports/backend_src_main_java_com_example_Application_java_analysis_20251206_211500.md

...

================================================================================
📈 分析统计
================================================================================
扫描的文件总数: 15
成功分析: 15
跳过的文件: 0
失败的文件: 0
总文件大小: 234.56 KB
================================================================================

✓ 汇总报告已保存: analysis_reports/summary_20251206_211500.md
✓ JSON 报告已保存: analysis_reports/summary_20251206_211500.json
```

## 进阶用法

### 集成到 Git Hook

在 `.git/hooks/pre-commit` 中添加：

```bash
#!/bin/bash
python3 src/directory_scanner.py . -o pre_commit_analysis -e .java
```

### 定期代码审查

使用 cron 定期运行：

```bash
# 每周一凌晨 2 点运行
0 2 * * 1 cd /path/to/project && python3 src/directory_scanner.py . -o weekly_analysis
```

## 技术支持

如有问题，请检查：
1. Ollama 服务状态
2. Python 依赖是否安装
3. 目录权限是否正确
4. 查看生成的 JSON 报告获取详细错误信息
