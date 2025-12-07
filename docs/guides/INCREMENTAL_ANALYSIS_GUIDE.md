# 增量代码分析指南

## 📖 概述

增量代码分析器是一个智能工具，它只分析新增或修改的代码文件，避免重复分析未更改的文件。这大大提高了分析效率，特别是在大型项目中。

## ✨ 核心特性

- **🎯 智能变更检测** - 自动识别新增和修改的文件
- **📦 缓存管理** - 维护已分析文件的缓存，避免重复工作
- **🔍 双重检测模式** - 支持 Git 变更检测和文件哈希检测
- **⚡ 高效分析** - 只分析需要的文件，节省时间和资源
- **📊 详细报告** - 生成包含变更统计的增量分析报告
- **🔄 灵活控制** - 支持强制全量分析和缓存管理

## 🚀 快速开始

### 基本用法

```bash
# 增量分析当前项目
python3 src/incremental_analyzer.py . -o incremental_reports

# 增量分析指定目录
python3 src/incremental_analyzer.py /path/to/project -o reports
```

### 首次运行

首次运行时，所有文件都会被视为"新文件"并进行分析：

```bash
python3 src/incremental_analyzer.py examples/ -o incremental_reports
```

输出示例：
```
🚀 增量代码分析器
================================================================================
项目目录: /path/to/examples
输出目录: /path/to/incremental_reports
缓存目录: /path/to/incremental_reports/.cache
================================================================================

📦 缓存信息:
  - 已缓存文件: 0
  - 上次更新: 从未

🔍 开始扫描项目文件...
✓ 扫描完成，找到 3 个文件

📈 文件分类统计:
  - 总文件数: 3
  - 新文件: 3
  - 已修改: 0
  - 未更改: 0

🎯 将分析 3 个文件
```

### 后续运行

再次运行时，只会分析新增或修改的文件：

```bash
python3 src/incremental_analyzer.py examples/ -o incremental_reports
```

如果没有文件更改：
```
📈 文件分类统计:
  - 总文件数: 3
  - 新文件: 0
  - 已修改: 0
  - 未更改: 3

✅ 没有需要分析的文件！所有文件都是最新的。
```

## 📋 命令行参数

### 必需参数

- `directory` - 要分析的项目目录路径

### 可选参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-o, --output` | 分析报告输出目录 | `-o reports` |
| `-c, --cache-dir` | 缓存目录（默认为输出目录/.cache） | `-c .cache` |
| `-e, --extensions` | 要分析的文件扩展名 | `-e .py .java` |
| `--force` | 强制分析所有文件，忽略缓存 | `--force` |
| `--no-git` | 不使用 Git 检测变更 | `--no-git` |
| `--show-cache` | 显示缓存信息 | `--show-cache` |
| `--clear-cache` | 清空缓存 | `--clear-cache` |

## 💡 使用场景

### 场景 1: 日常开发中的增量分析

在开发过程中，每次提交代码后运行增量分析：

```bash
# 修改了一些代码文件
git add .
git commit -m "Update feature X"

# 只分析修改的文件
python3 src/incremental_analyzer.py . -o reports
```

### 场景 2: 只分析特定类型的文件

```bash
# 只分析 Python 文件
python3 src/incremental_analyzer.py . -o reports -e .py

# 只分析 Java 和 JavaScript 文件
python3 src/incremental_analyzer.py . -o reports -e .java .js
```

### 场景 3: 强制重新分析所有文件

当需要重新分析所有文件时（例如，更新了分析规则）：

```bash
python3 src/incremental_analyzer.py . -o reports --force
```

### 场景 4: 非 Git 项目的增量分析

对于非 Git 项目，使用文件哈希检测：

```bash
python3 src/incremental_analyzer.py /path/to/project -o reports --no-git
```

### 场景 5: 查看和管理缓存

```bash
# 查看缓存信息
python3 src/incremental_analyzer.py . --show-cache

# 清空缓存（下次运行将分析所有文件）
python3 src/incremental_analyzer.py . --clear-cache
```

## 🔍 变更检测机制

### Git 模式（默认）

当项目是 Git 仓库时，增量分析器会：

1. 检测 Git 仓库
2. 获取最近提交中的变更文件列表
3. 将这些文件标记为"已修改"
4. 结合缓存信息，确定需要分析的文件

**优点**：
- 精确检测 Git 跟踪的变更
- 与版本控制系统集成
- 适合团队协作

### 文件哈希模式

当项目不是 Git 仓库或使用 `--no-git` 参数时：

1. 计算每个文件的 MD5 哈希值
2. 与缓存中的哈希值比较
3. 哈希值不同则视为已修改

**优点**：
- 不依赖 Git
- 适用于任何项目
- 精确检测文件内容变化

## 📊 输出文件

### 1. 分析报告

每个分析的文件都会生成独立的分析报告：

```
incremental_reports/
├── Test_java_analysis_20231207_143022.md
├── Application_java_analysis_20231207_143045.md
└── ...
```

### 2. 增量报告

每次运行都会生成一个增量分析报告：

```
incremental_reports/
└── incremental_report_20231207_143100.md
```

报告内容包括：
- 统计信息（新文件、已修改、未更改）
- 新文件列表
- 已修改文件列表
- 分析结果摘要

示例：

```markdown
# 增量代码分析报告

**项目目录**: `/path/to/project`
**分析时间**: 2023-12-07 14:31:00
**分析模式**: Git 变更检测

## 📊 统计信息

- 扫描的文件总数: 10
- 新文件: 2
- 已修改文件: 3
- 未更改文件: 5
- 成功分析: 5
- 分析失败: 0

## 🆕 新文件

- `src/new_feature.py`
- `src/utils/helper.py`

## ✏️ 已修改文件

- `src/main.py`
- `src/analyzer.py`
- `tests/test_main.py`
```

### 3. 缓存文件

缓存信息存储在 JSON 文件中：

```
incremental_reports/.cache/
└── analysis_cache.json
```

缓存内容示例：

```json
{
  "version": "1.0",
  "last_update": "2023-12-07T14:31:00.123456",
  "files": {
    "/absolute/path/to/file.py": {
      "hash": "5d41402abc4b2a76b9719d911017c592",
      "last_analyzed": "2023-12-07T14:31:00.123456",
      "status": "success",
      "language": "Python"
    }
  }
}
```

## 🛠️ 高级用法

### 自定义缓存位置

```bash
# 将缓存存储在项目根目录的 .analysis_cache 中
python3 src/incremental_analyzer.py . -o reports -c .analysis_cache
```

### 集成到 CI/CD 流程

```bash
#!/bin/bash
# ci-analyze.sh

# 拉取最新代码
git pull

# 运行增量分析
python3 src/incremental_analyzer.py . -o ci_reports

# 检查是否有分析失败
if [ $? -ne 0 ]; then
    echo "代码分析失败！"
    exit 1
fi

echo "代码分析完成！"
```

### 定期全量分析

建议定期运行全量分析以确保所有文件都是最新的：

```bash
# 每周运行一次全量分析
0 0 * * 0 cd /path/to/project && python3 src/incremental_analyzer.py . -o reports --force
```

## 🔧 故障排除

### 问题 1: 缓存损坏

**症状**: 运行时出现缓存加载错误

**解决方案**:
```bash
# 清空缓存重新开始
python3 src/incremental_analyzer.py . --clear-cache
```

### 问题 2: Git 检测失败

**症状**: 显示"不是 Git 仓库"警告

**解决方案**:
```bash
# 使用文件哈希模式
python3 src/incremental_analyzer.py . -o reports --no-git
```

### 问题 3: 文件未被检测为已修改

**症状**: 修改了文件但未被分析

**解决方案**:
```bash
# 强制重新分析
python3 src/incremental_analyzer.py . -o reports --force
```

## 📈 性能优化

### 大型项目优化建议

1. **限制文件类型**: 只分析需要的文件类型
   ```bash
   python3 src/incremental_analyzer.py . -o reports -e .py .java
   ```

2. **使用 Git 模式**: 在 Git 仓库中，Git 模式比哈希模式更快
   ```bash
   # 默认已启用 Git 模式
   python3 src/incremental_analyzer.py . -o reports
   ```

3. **定期清理缓存**: 删除不再存在的文件的缓存
   ```bash
   # 清空缓存后重新运行
   python3 src/incremental_analyzer.py . --clear-cache
   python3 src/incremental_analyzer.py . -o reports
   ```

## 🔄 与其他工具集成

### 与 Web 界面集成

增量分析器可以与 Web 界面集成：

```python
from src.incremental_analyzer import IncrementalAnalyzer

# 在 Flask 路由中使用
@app.route('/api/analyze/incremental', methods=['POST'])
def analyze_incremental():
    analyzer = IncrementalAnalyzer(
        root_dir=request.json['directory'],
        output_dir='web_reports'
    )
    results = analyzer.analyze_incremental()
    return jsonify(results)
```

### 与 REST API 集成

在 API 服务器中添加增量分析端点：

```python
# api/server.py
from src.incremental_analyzer import IncrementalAnalyzer

@app.route('/api/v1/analyze/incremental', methods=['POST'])
def incremental_analysis():
    data = request.json
    analyzer = IncrementalAnalyzer(
        root_dir=data['directory'],
        output_dir='api_reports'
    )
    results = analyzer.analyze_incremental(force_all=data.get('force', False))
    return jsonify({
        'status': 'success',
        'results': results,
        'stats': analyzer.stats
    })
```

## 📚 API 参考

### IncrementalAnalyzer 类

```python
class IncrementalAnalyzer:
    def __init__(self, root_dir: str, output_dir: str = None, 
                 cache_dir: str = None, extensions: List[str] = None, 
                 use_git: bool = True)
```

**参数**:
- `root_dir`: 项目根目录
- `output_dir`: 分析报告输出目录
- `cache_dir`: 缓存目录
- `extensions`: 要分析的文件扩展名列表
- `use_git`: 是否使用 Git 检测变更

**主要方法**:

```python
# 执行增量分析
results = analyzer.analyze_incremental(force_all=False, verbose=True)

# 清空缓存
analyzer.clear_cache()

# 显示缓存信息
analyzer.show_cache_info()
```

### AnalysisCache 类

```python
class AnalysisCache:
    def __init__(self, cache_dir: str)
```

**主要方法**:

```python
# 检查文件是否已更改
is_changed = cache.is_file_changed(file_path)

# 更新文件缓存
cache.update_file_cache(file_path, analysis_result)

# 获取缓存统计
stats = cache.get_statistics()

# 清空缓存
cache.clear_cache()
```

## 🎯 最佳实践

1. **定期运行增量分析**: 在每次代码提交后运行
2. **定期全量分析**: 每周或每月运行一次全量分析
3. **备份缓存**: 在重要的里程碑备份缓存文件
4. **监控缓存大小**: 定期检查缓存大小，必要时清理
5. **使用 Git 模式**: 在 Git 仓库中优先使用 Git 模式
6. **限制文件类型**: 只分析需要的文件类型以提高效率

## 🔗 相关文档

- [目录扫描器指南](DIRECTORY_SCANNER_GUIDE.md)
- [LangChain 智能代理指南](LANGCHAIN_AGENT_GUIDE.md)
- [Docker 部署指南](DOCKER_DEPLOY.md)
- [API 文档](../../api/API_DOCS.md)

## 📝 更新日志

### v1.0.0 (2023-12-07)

- ✅ 初始版本发布
- ✅ 支持 Git 变更检测
- ✅ 支持文件哈希检测
- ✅ 缓存管理功能
- ✅ 增量分析报告生成
- ✅ 命令行界面
