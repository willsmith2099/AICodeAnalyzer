# 代码知识图谱构建报告

**构建时间**: 2025-12-07 11:39:49

## 📊 扫描统计

- 扫描的文件总数: 2
- 成功解析: 2
- 跳过的文件: 0
- 失败的文件: 0
- 总文件大小: 1.59 KB
- 提取的类: 4
- 提取的方法: 11

## 🗄️ 图数据库统计

- 文件节点: 2
- 类节点: 5
- 方法节点: 11
- 调用关系: 0
- 继承关系: 1

## 🔍 查询示例

### 查看所有类

```cypher
MATCH (c:Class) RETURN c.name, c.file_path LIMIT 10
```

### 查看类的方法

```cypher
MATCH (c:Class)-[:HAS_METHOD]->(m:Method)
RETURN c.name, collect(m.name) as methods
```

### 查看继承关系

```cypher
MATCH (child:Class)-[:EXTENDS]->(parent:Class)
RETURN child.name, parent.name
```

### 查看方法调用链

```cypher
MATCH (m1:Method)-[:CALLS]->(m2:Method)
RETURN m1.class_name + '.' + m1.name as caller,
       m2.class_name + '.' + m2.name as callee
```

