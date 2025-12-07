# 增量代码分析 - 快速参考

## 🚀 快速开始

```bash
# 基本用法
python3 src/incremental_analyzer.py <目录> -o <输出目录>

# 示例
python3 src/incremental_analyzer.py . -o incremental_reports
```

## 📋 常用命令

| 命令 | 说明 |
|------|------|
| `python3 src/incremental_analyzer.py . -o reports` | 增量分析当前目录 |
| `python3 src/incremental_analyzer.py . -o reports --force` | 强制分析所有文件 |
| `python3 src/incremental_analyzer.py . -o reports -e .py .java` | 只分析 Python 和 Java 文件 |
| `python3 src/incremental_analyzer.py . --show-cache` | 查看缓存信息 |
| `python3 src/incremental_analyzer.py . --clear-cache` | 清空缓存 |
| `python3 src/incremental_analyzer.py . -o reports --no-git` | 使用文件哈希模式 |

## 🎯 使用场景

### 场景 1: 日常开发
```bash
# 修改代码后运行
git commit -m "Update feature"
python3 src/incremental_analyzer.py . -o reports
```

### 场景 2: 首次分析
```bash
# 首次运行会分析所有文件
python3 src/incremental_analyzer.py /path/to/project -o reports
```

### 场景 3: 定期全量分析
```bash
# 每周运行一次全量分析
python3 src/incremental_analyzer.py . -o reports --force
```

### 场景 4: 特定文件类型
```bash
# 只分析 Java 文件
python3 src/incremental_analyzer.py . -o reports -e .java
```

## 📊 输出文件

```
incremental_reports/
├── .cache/
│   └── analysis_cache.json          # 缓存文件
├── incremental_report_*.md          # 增量分析报告
├── *_analysis_*.md                  # 各文件的分析报告
└── summary_*.md                     # 汇总报告
```

## 🔍 工作原理

### Git 模式（默认）
1. 检测 Git 仓库
2. 获取变更文件列表
3. 结合缓存确定需要分析的文件

### 哈希模式
1. 计算文件 MD5 哈希
2. 与缓存中的哈希比对
3. 哈希不同则视为已修改

## 💡 最佳实践

1. ✅ **定期运行** - 每次代码提交后运行增量分析
2. ✅ **定期全量** - 每周或每月运行一次全量分析
3. ✅ **备份缓存** - 在重要里程碑备份缓存文件
4. ✅ **限制类型** - 只分析需要的文件类型
5. ✅ **使用 Git** - 在 Git 仓库中优先使用 Git 模式

## 🔧 故障排除

| 问题 | 解决方案 |
|------|----------|
| 缓存损坏 | `python3 src/incremental_analyzer.py . --clear-cache` |
| Git 检测失败 | `python3 src/incremental_analyzer.py . -o reports --no-git` |
| 文件未被检测 | `python3 src/incremental_analyzer.py . -o reports --force` |

## 📚 详细文档

- [完整使用指南](INCREMENTAL_ANALYSIS_GUIDE.md)
- [实现总结](../reports/INCREMENTAL_ANALYSIS_IMPLEMENTATION.md)
- [项目主文档](../../README.md)

## 🎨 示例代码

### Python API
```python
from src.incremental_analyzer import IncrementalAnalyzer

# 创建分析器
analyzer = IncrementalAnalyzer(
    root_dir='.',
    output_dir='reports',
    extensions=['.py', '.java']
)

# 执行分析
results = analyzer.analyze_incremental()

# 查看统计
print(f"分析了 {len(results)} 个文件")
print(f"统计: {analyzer.stats}")
```

### 缓存管理
```python
# 查看缓存信息
analyzer.show_cache_info()

# 清空缓存
analyzer.clear_cache()

# 获取缓存统计
stats = analyzer.cache.get_statistics()
```

## ⚡ 性能对比

| 场景 | 传统分析 | 增量分析 | 提升 |
|------|----------|----------|------|
| 100 文件项目（首次） | 10 分钟 | 10 分钟 | 0% |
| 100 文件项目（5 个修改） | 10 分钟 | 30 秒 | 95% |
| 1000 文件项目（10 个修改） | 100 分钟 | 1 分钟 | 99% |

---

**版本**: v1.0.0  
**更新**: 2023-12-07
