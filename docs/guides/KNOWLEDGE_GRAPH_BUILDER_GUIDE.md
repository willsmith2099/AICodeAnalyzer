# 代码知识图谱构建指南

## 📖 概述

代码知识图谱构建器是一个强大的工具，它能够扫描指定目录下的代码工程，自动提取代码结构信息（类、方法、继承关系等），并将这些信息构建成可查询的知识图谱存储在 Neo4j 图数据库中。

## ✨ 核心特性

- **🔍 智能代码扫描** - 递归扫描目录，支持多种编程语言
- **📊 结构提取** - 自动提取类、方法、继承关系、接口实现等
- **🗄️ 图数据库存储** - 将代码结构存储为 Neo4j 知识图谱
- **🔗 关系映射** - 自动建立类继承、方法调用等关系
- **📈 统计分析** - 提供详细的构建统计和图数据统计
- **📝 报告生成** - 自动生成构建报告和查询示例

## 🚀 快速开始

### 前置要求

1. **Neo4j 数据库**
   ```bash
   # 使用 Docker 启动 Neo4j
   cd docker
   docker-compose up -d neo4j
   ```

2. **Python 依赖**
   ```bash
   pip install neo4j
   ```

### 基本用法

```bash
# 构建当前目录的知识图谱
python3 src/knowledge_graph_builder.py . -o graph_report.md

# 构建指定目录
python3 src/knowledge_graph_builder.py /path/to/project -o report.md
```

### 首次运行示例

```bash
# 分析 examples 目录
python3 src/knowledge_graph_builder.py examples/ -o examples_graph_report.md
```

输出示例：
```
🚀 代码知识图谱构建器
================================================================================
项目目录: examples/
================================================================================

✓ 成功连接到 Neo4j 数据库: bolt://localhost:7687

📊 创建数据库索引...
✓ 索引创建完成

🔍 开始扫描目录: /path/to/examples
📝 支持的文件类型: .java, .py, .js, .ts

✓ 扫描完成，找到 3 个文件
  总大小: 12.5 KB

🔨 开始构建知识图谱...

[1/3] 解析: Test.java
  ✓ 成功 - 找到 1 个类
[2/3] 解析: Application.java
  ✓ 成功 - 找到 1 个类
[3/3] 解析: langchain_agent_demo.py
  ✓ 成功 - 找到 0 个类

================================================================================
📊 构建统计
================================================================================
扫描的文件总数: 3
成功解析: 3
跳过的文件: 0
失败的文件: 0
总文件大小: 12.5 KB
提取的类: 2
提取的方法: 8
================================================================================
```

## 📋 命令行参数

### 必需参数

- `directory` - 要扫描的项目目录路径

### 可选参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `-o, --output` | 构建报告输出文件 | 无 | `-o report.md` |
| `-e, --extensions` | 要扫描的文件扩展名 | `.java .py .js .ts` | `-e .java .py` |
| `--clear` | 清空现有图数据 | False | `--clear` |
| `--uri` | Neo4j 连接 URI | `bolt://localhost:7687` | `--uri bolt://localhost:7687` |
| `--user` | Neo4j 用户名 | `neo4j` | `--user neo4j` |
| `--password` | Neo4j 密码 | `password` | `--password mypassword` |
| `--export` | 导出统计数据到 JSON | 无 | `--export stats.json` |
| `--max-size` | 最大文件大小（字节） | 1048576 (1MB) | `--max-size 2097152` |

## 💡 使用场景

### 场景 1: 分析新项目

```bash
# 首次分析项目，清空现有数据
python3 src/knowledge_graph_builder.py /path/to/project --clear -o report.md
```

### 场景 2: 只分析特定语言

```bash
# 只分析 Java 文件
python3 src/knowledge_graph_builder.py . -e .java -o java_graph.md

# 只分析 Python 和 JavaScript 文件
python3 src/knowledge_graph_builder.py . -e .py .js -o py_js_graph.md
```

### 场景 3: 增量更新图谱

```bash
# 不清空现有数据，增量添加新文件
python3 src/knowledge_graph_builder.py . -o update_report.md
```

### 场景 4: 导出统计数据

```bash
# 构建图谱并导出统计数据
python3 src/knowledge_graph_builder.py . -o report.md --export stats.json
```

### 场景 5: 自定义 Neo4j 连接

```bash
# 连接到远程 Neo4j 服务器
python3 src/knowledge_graph_builder.py . \
  --uri bolt://remote-server:7687 \
  --user myuser \
  --password mypassword \
  -o report.md
```

## 🗄️ 知识图谱结构

### 节点类型

#### 1. File 节点
表示源代码文件

**属性**:
- `path`: 文件路径
- `language`: 编程语言
- `metadata`: 其他元数据

#### 2. Class 节点
表示类或接口

**属性**:
- `name`: 类名
- `file_path`: 所在文件路径
- `line_start`: 起始行号
- `line_end`: 结束行号
- `metadata`: 修饰符、注解等

#### 3. Method 节点
表示方法或函数

**属性**:
- `name`: 方法名
- `class_name`: 所属类名
- `file_path`: 所在文件路径
- `line_start`: 起始行号
- `line_end`: 结束行号
- `parameters`: 参数列表
- `return_type`: 返回类型
- `metadata`: 修饰符、注解等

#### 4. Interface 节点
表示接口

**属性**:
- `name`: 接口名

### 关系类型

#### 1. CONTAINS
文件包含类

```
(File)-[:CONTAINS]->(Class)
```

#### 2. HAS_METHOD
类拥有方法

```
(Class)-[:HAS_METHOD]->(Method)
```

#### 3. EXTENDS
类继承关系

```
(ChildClass)-[:EXTENDS]->(ParentClass)
```

#### 4. IMPLEMENTS
类实现接口

```
(Class)-[:IMPLEMENTS]->(Interface)
```

#### 5. CALLS
方法调用关系

```
(CallerMethod)-[:CALLS]->(CalleeMethod)
```

## 🔍 查询示例

### 基本查询

#### 查看所有类

```cypher
MATCH (c:Class)
RETURN c.name, c.file_path
LIMIT 10
```

#### 查看所有方法

```cypher
MATCH (m:Method)
RETURN m.name, m.class_name, m.return_type
LIMIT 10
```

#### 查看文件统计

```cypher
MATCH (f:File)
RETURN f.language, count(*) as count
```

### 结构查询

#### 查看类的所有方法

```cypher
MATCH (c:Class {name: 'MyClass'})-[:HAS_METHOD]->(m:Method)
RETURN c.name, collect(m.name) as methods
```

#### 查看类的继承层次

```cypher
MATCH path = (c:Class {name: 'MyClass'})-[:EXTENDS*]->(parent:Class)
RETURN path
```

#### 查看接口实现

```cypher
MATCH (c:Class)-[:IMPLEMENTS]->(i:Interface)
RETURN c.name as class, i.name as interface
```

### 关系查询

#### 查看方法调用链

```cypher
MATCH (m1:Method)-[:CALLS]->(m2:Method)
RETURN m1.class_name + '.' + m1.name as caller,
       m2.class_name + '.' + m2.name as callee
LIMIT 20
```

#### 查看深度调用链

```cypher
MATCH path = (m1:Method {name: 'main'})-[:CALLS*1..3]->(m2:Method)
RETURN path
LIMIT 10
```

#### 查找被调用最多的方法

```cypher
MATCH (m:Method)<-[:CALLS]-(caller:Method)
RETURN m.class_name + '.' + m.name as method, count(caller) as call_count
ORDER BY call_count DESC
LIMIT 10
```

### 分析查询

#### 查找没有方法的类

```cypher
MATCH (c:Class)
WHERE NOT (c)-[:HAS_METHOD]->()
RETURN c.name, c.file_path
```

#### 查找最复杂的类（方法最多）

```cypher
MATCH (c:Class)-[:HAS_METHOD]->(m:Method)
RETURN c.name, count(m) as method_count
ORDER BY method_count DESC
LIMIT 10
```

#### 查找继承深度最深的类

```cypher
MATCH path = (c:Class)-[:EXTENDS*]->(parent:Class)
RETURN c.name, length(path) as depth
ORDER BY depth DESC
LIMIT 10
```

## 📊 输出文件

### 1. 构建报告 (Markdown)

生成的报告包含：
- 扫描统计信息
- 图数据库统计
- 常用查询示例

示例：
```markdown
# 代码知识图谱构建报告

**构建时间**: 2023-12-07 10:00:00

## 📊 扫描统计

- 扫描的文件总数: 50
- 成功解析: 48
- 跳过的文件: 1
- 失败的文件: 1
- 总文件大小: 256.5 KB
- 提取的类: 35
- 提取的方法: 180

## 🗄️ 图数据库统计

- 文件节点: 48
- 类节点: 35
- 方法节点: 180
- 调用关系: 120
- 继承关系: 15
```

### 2. 统计数据 (JSON)

导出的 JSON 文件包含详细的统计数据：

```json
{
  "timestamp": "2023-12-07T10:00:00",
  "scan_statistics": {
    "total_files": 50,
    "parsed_files": 48,
    "skipped_files": 1,
    "failed_files": 1,
    "total_classes": 35,
    "total_methods": 180,
    "total_size": 262656
  },
  "graph_statistics": {
    "files": 48,
    "classes": 35,
    "methods": 180,
    "calls": 120,
    "inheritance": 15
  }
}
```

## 🛠️ 高级用法

### Python API 使用

```python
from src.knowledge_graph_builder import KnowledgeGraphBuilder

# 创建构建器
builder = KnowledgeGraphBuilder(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    extensions=['.java', '.py']
)

# 构建知识图谱
results = builder.build_graph(
    root_dir='/path/to/project',
    clear_existing=True
)

# 生成报告
builder.generate_report('graph_report.md')

# 导出统计数据
builder.export_graph_data('graph_stats.json')

# 关闭连接
builder.close()
```

### 与 Neo4j 客户端集成

```python
from src.graph.neo4j_client import Neo4jClient

# 创建客户端
client = Neo4jClient()

# 查询类的方法
methods = client.get_class_methods('MyClass')
print(f"方法: {methods}")

# 查询方法调用
calls = client.get_method_calls('processData', 'MyClass')
print(f"调用: {calls}")

# 查询类层次结构
hierarchy = client.get_class_hierarchy('MyClass')
print(f"层次: {hierarchy}")

# 获取统计信息
stats = client.get_statistics()
print(f"统计: {stats}")

# 关闭连接
client.close()
```

## 🎨 可视化

### Neo4j 浏览器

1. 访问 http://localhost:7474
2. 使用用户名和密码登录
3. 运行 Cypher 查询

### 可视化示例

#### 查看整体结构

```cypher
MATCH (f:File)-[:CONTAINS]->(c:Class)-[:HAS_METHOD]->(m:Method)
RETURN f, c, m
LIMIT 50
```

#### 查看继承关系图

```cypher
MATCH path = (c1:Class)-[:EXTENDS]->(c2:Class)
RETURN path
```

#### 查看方法调用网络

```cypher
MATCH path = (m1:Method)-[:CALLS]->(m2:Method)
RETURN path
LIMIT 100
```

## 🔧 故障排除

### 问题 1: 无法连接到 Neo4j

**症状**: `无法连接到 Neo4j 数据库`

**解决方案**:
```bash
# 检查 Neo4j 是否运行
docker ps | grep neo4j

# 启动 Neo4j
cd docker
docker-compose up -d neo4j

# 检查连接参数
python3 src/knowledge_graph_builder.py . --uri bolt://localhost:7687 --user neo4j --password password
```

### 问题 2: 解析失败

**症状**: 某些文件解析失败

**解决方案**:
- 检查文件编码是否为 UTF-8
- 检查文件大小是否超过限制
- 查看错误日志了解具体原因

### 问题 3: 图数据重复

**症状**: 多次运行导致数据重复

**解决方案**:
```bash
# 清空现有数据重新构建
python3 src/knowledge_graph_builder.py . --clear -o report.md
```

## 📈 性能优化

### 大型项目优化

1. **限制文件类型**
   ```bash
   python3 src/knowledge_graph_builder.py . -e .java
   ```

2. **增加文件大小限制**
   ```bash
   python3 src/knowledge_graph_builder.py . --max-size 2097152
   ```

3. **分批处理**
   ```bash
   # 先处理核心模块
   python3 src/knowledge_graph_builder.py src/core -o core_report.md
   
   # 再处理其他模块
   python3 src/knowledge_graph_builder.py src/utils -o utils_report.md
   ```

## 🎯 最佳实践

1. **首次构建使用 --clear**
   ```bash
   python3 src/knowledge_graph_builder.py . --clear -o report.md
   ```

2. **定期更新图谱**
   ```bash
   # 每天或每次重大更新后运行
   python3 src/knowledge_graph_builder.py . -o daily_report.md
   ```

3. **导出统计数据**
   ```bash
   # 保存统计数据用于分析
   python3 src/knowledge_graph_builder.py . --export stats_$(date +%Y%m%d).json
   ```

4. **备份图数据**
   ```bash
   # 定期备份 Neo4j 数据
   docker-compose exec neo4j neo4j-admin dump --to=/backups/graph.dump
   ```

5. **优化查询性能**
   - 使用索引（自动创建）
   - 限制查询结果数量
   - 使用参数化查询

## 🔗 相关文档

- [Neo4j 使用指南](NEO4J_GUIDE.md)
- [代码解析器文档](../../src/graph/code_parser.py)
- [Neo4j 客户端文档](../../src/graph/neo4j_client.py)
- [项目主文档](../../README.md)

## 📝 更新日志

### v1.0.0 (2023-12-07)

- ✅ 初始版本发布
- ✅ 支持 Java, Python, JavaScript, TypeScript
- ✅ 自动提取类、方法、继承关系
- ✅ Neo4j 图数据库集成
- ✅ 构建报告生成
- ✅ 统计数据导出
- ✅ 完整的命令行界面

---

**版本**: v1.0.0  
**更新**: 2023-12-07
