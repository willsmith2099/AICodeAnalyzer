# AST 静态分析和 Git 变更影响追踪

## 概述

本模块实现了基于 AST（抽象语法树）的静态代码分析，结合 Git Diff 追踪代码变更的影响链。

## 核心功能

### 1. AST 静态分析 (`ast_analyzer.py`)

#### 功能特性
- ✅ **Python AST 分析**: 使用 Python 内置 `ast` 模块
- ✅ **Java 代码分析**: 基于正则表达式（可扩展为 JavaParser）
- ✅ **依赖关系提取**: 类继承、方法调用、接口实现
- ✅ **影响链追踪**: 向上（调用者）和向下（被调用者）
- ✅ **依赖图构建**: 完整的项目依赖关系图

#### 支持的分析
- 类定义和继承关系
- 方法定义和调用关系
- 导入和依赖关系
- 接口实现关系
- 变量和字段定义

### 2. Git 变更分析 (`git_change_analyzer.py`)

#### 功能特性
- ✅ **Git Diff 解析**: 提取变更的文件和代码行
- ✅ **变更点识别**: 识别变更的类、方法、变量
- ✅ **影响链追踪**: 结合 AST 分析追踪影响范围
- ✅ **报告生成**: Markdown 格式的影响分析报告

#### 支持的操作
- 获取变更文件列表
- 解析文件详细变更
- 提取变更的代码项目
- 构建完整依赖图
- 生成影响分析报告

## 技术原理

### 静态分析流程

```
1. 代码解析
   ↓
2. 生成 AST
   ↓
3. 提取结构信息
   ↓
4. 构建依赖关系
   ↓
5. 追踪影响链
```

### Git 变更分析流程

```
1. Git Diff 获取变更
   ↓
2. 解析变更的代码行
   ↓
3. AST 分析识别变更项
   ↓
4. 构建项目依赖图
   ↓
5. 追踪影响链
   ↓
6. 生成分析报告
```

## 使用方法

### 方法 1: Python AST 分析

```python
from src.ast_analyzer import ASTAnalyzer

# 创建分析器
analyzer = ASTAnalyzer(language='Python')

# 分析单个文件
result = analyzer.analyze_file('path/to/file.py')

print(f"类数量: {len(result['classes'])}")
print(f"函数数量: {len(result['functions'])}")
print(f"导入数量: {len(result['imports'])}")

# 查看类信息
for cls in result['classes']:
    print(f"类: {cls['name']}")
    print(f"  方法: {[m['name'] for m in cls['methods']]}")
```

### 方法 2: Java 代码分析

```python
from src.ast_analyzer import ASTAnalyzer

# 创建 Java 分析器
analyzer = ASTAnalyzer(language='Java')

# 分析 Java 文件
result = analyzer.analyze_file('path/to/Service.java')

print(f"包名: {result['package']}")
print(f"导入: {result['imports']}")

for cls in result['classes']:
    print(f"类: {cls['name']}")
    if cls['parent']:
        print(f"  继承: {cls['parent']}")
    if cls['interfaces']:
        print(f"  实现: {cls['interfaces']}")
```

### 方法 3: 构建依赖图

```python
from src.ast_analyzer import ASTAnalyzer

analyzer = ASTAnalyzer(language='Python')

# 分析多个文件
files = ['file1.py', 'file2.py', 'file3.py']
dependency_graph = analyzer.build_dependency_graph(files)

# 查看依赖关系
for item, deps in dependency_graph['dependencies'].items():
    print(f"{item} -> {deps}")

# 查看继承关系
for child, parents in dependency_graph['inheritance'].items():
    print(f"{child} extends {parents}")
```

### 方法 4: 影响链追踪

```python
from src.ast_analyzer import ASTAnalyzer

analyzer = ASTAnalyzer(language='Python')

# 构建依赖图
analyzer.build_dependency_graph(files)

# 追踪变更影响
changed_items = ['UserService.py::UserService.create_user']
impact = analyzer.trace_impact(changed_items, max_depth=5)

print(f"受影响项目总数: {impact['total_affected']}")

# 查看上游影响（谁会受影响）
for item in changed_items:
    upstream = impact['upstream_impact'][item]
    print(f"\n{item} 的上游影响:")
    for chain in upstream:
        print(f"  {' ← '.join(chain)}")

# 查看下游影响（依赖哪些）
for item in changed_items:
    downstream = impact['downstream_impact'][item]
    print(f"\n{item} 的下游影响:")
    for chain in downstream:
        print(f"  {' → '.join(chain)}")
```

### 方法 5: Git 变更分析

```python
from src.git_change_analyzer import GitChangeAnalyzer

# 创建 Git 分析器
analyzer = GitChangeAnalyzer('/path/to/repo', language='Python')

# 获取变更文件
changed_files = analyzer.get_changed_files('HEAD~1..HEAD')
print(f"变更文件: {changed_files}")

# 分析变更影响
result = analyzer.analyze_change_impact('HEAD~1..HEAD', max_depth=5)

print(f"摘要: {result['summary']}")
print(f"受影响项目: {result['impact']['total_affected']}")

# 生成报告
report = analyzer.generate_report(result, 'impact_report.md')
```

### 方法 6: 命令行使用

```bash
# Python 分析
python src/ast_analyzer.py

# Git 变更分析
python src/git_change_analyzer.py /path/to/repo HEAD~1..HEAD

# 运行示例
python examples/ast_analysis_demo.py
```

## 使用场景

### 场景 1: 代码审查

```python
# 分析最近的代码变更
analyzer = GitChangeAnalyzer('.', language='Java')
result = analyzer.analyze_change_impact('HEAD~1..HEAD')

# 生成审查报告
analyzer.generate_report(result, 'code_review_report.md')
```

### 场景 2: 影响评估

```python
# 评估重构的影响范围
analyzer = ASTAnalyzer(language='Python')
analyzer.build_dependency_graph(all_files)

changed_items = ['core/database.py::Database.connect']
impact = analyzer.trace_impact(changed_items, max_depth=10)

print(f"重构将影响 {impact['total_affected']} 个项目")
```

### 场景 3: 测试范围确定

```python
# 确定需要测试的范围
analyzer = GitChangeAnalyzer('.', language='Java')
result = analyzer.analyze_change_impact('feature-branch..main')

# 提取受影响的类和方法
affected_items = set()
for item in result['changed_items']:
    upstream = result['impact']['upstream_impact'][item]
    for chain in upstream:
        affected_items.update(chain)

print(f"需要测试的项目: {affected_items}")
```

### 场景 4: 依赖分析

```python
# 分析模块间依赖
analyzer = ASTAnalyzer(language='Python')
dependency_graph = analyzer.build_dependency_graph(all_files)

# 找出高耦合模块
for item, deps in dependency_graph['dependencies'].items():
    if len(deps) > 10:
        print(f"高耦合模块: {item} (依赖 {len(deps)} 个模块)")
```

## 输出示例

### AST 分析结果

```json
{
  "file": "UserService.py",
  "classes": [
    {
      "name": "UserService",
      "line": 10,
      "bases": ["BaseService"],
      "methods": [
        {
          "name": "create_user",
          "line": 15,
          "args": ["self", "name"]
        }
      ]
    }
  ],
  "imports": ["database", "models.User"],
  "calls": ["Database", "User", "validate_user"]
}
```

### 影响分析报告

```markdown
# Git 代码变更影响分析报告

**Commit 范围**: `HEAD~1..HEAD`
**分析时间**: 2025-12-08 21:06:59
**编程语言**: Python

## 摘要

变更了 3 个文件，新增 150 行，删除 45 行，影响 12 个项目

## 变更文件

### `src/user_service.py`
- 新增行数: 80
- 删除行数: 20
- 变更项目: 2

变更的类/方法:
- `src/user_service.py::UserService`
- `src/user_service.py::UserService.create_user`

## 影响分析

### 变更: `src/user_service.py::UserService.create_user`

**上游影响** (谁会受影响):
1. api/user_controller.py::UserController.register
2. tests/test_user_service.py::TestUserService.test_create

**下游影响** (依赖哪些):
1. models/user.py::User
2. database/connection.py::Database.save

## 建议

基于影响分析，建议:
1. 重点测试受影响的 12 个项目
2. 检查上游调用者的兼容性
3. 验证下游依赖的可用性
4. 更新相关文档和测试用例
```

## 技术栈

### Python 分析
- **ast**: Python 内置 AST 模块
- **re**: 正则表达式
- **subprocess**: Git 命令执行

### Java 分析（当前实现）
- **re**: 正则表达式解析
- **可扩展**: JavaParser, ASM, JGit

### 未来扩展
- **JavaParser**: 完整的 Java AST 解析
- **tree-sitter**: 多语言通用解析器
- **srcML**: XML 格式的源代码表示

## 限制和注意事项

### 当前限制
1. Java 分析基于正则表达式，不如 AST 精确
2. 不支持动态调用和反射
3. 跨文件引用需要完整项目扫描
4. 大型项目可能需要较长分析时间

### 最佳实践
1. 先在小范围测试
2. 合理设置追踪深度
3. 定期更新依赖图
4. 结合单元测试验证

## 故障排查

### 问题 1: AST 解析失败

**原因**: 语法错误或不支持的语法

**解决方案**:
- 检查代码语法
- 更新 Python 版本
- 查看错误信息

### 问题 2: Git 命令失败

**原因**: 不是 Git 仓库或 Git 未安装

**解决方案**:
- 确认在 Git 仓库中运行
- 检查 Git 是否安装
- 验证 commit 范围有效

### 问题 3: 依赖关系不完整

**原因**: 未扫描所有文件

**解决方案**:
- 扫描完整项目
- 包含所有相关文件
- 检查文件路径正确

## 参考资料

- [Python AST 文档](https://docs.python.org/3/library/ast.html)
- [JavaParser](https://javaparser.org/)
- [Git Diff 格式](https://git-scm.com/docs/git-diff)
- [静态代码分析](https://en.wikipedia.org/wiki/Static_program_analysis)

## 示例代码

完整示例请参考:
- [ast_analysis_demo.py](../examples/ast_analysis_demo.py)
- [ast_analyzer.py](../src/ast_analyzer.py)
- [git_change_analyzer.py](../src/git_change_analyzer.py)
