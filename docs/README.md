# 文档目录

本目录包含项目的所有文档，按类别组织。

## 📁 目录结构

```
docs/
├── guides/          # 使用指南和教程
│   ├── DIRECTORY_SCANNER_GUIDE.md      # 目录扫描器使用指南
│   ├── LANGCHAIN_AGENT_GUIDE.md        # LangChain 智能代理指南
│   ├── AGENT_VERIFICATION_GUIDE.md     # 智能代理验证指南
│   ├── QUICKSTART_LANGCHAIN.md         # LangChain 快速开始
│   ├── DOCKER_DEPLOY.md                # Docker 部署指南
│   ├── NEO4J_GUIDE.md                  # Neo4j 使用指南
│   ├── INCREMENTAL_ANALYSIS_GUIDE.md   # 增量代码分析指南 ⚡⭐
│   └── INCREMENTAL_ANALYSIS_QUICKREF.md # 增量分析快速参考 ⚡
│
└── reports/         # 项目报告和总结
    ├── PROJECT_SUMMARY.md              # 项目总结
    ├── GIT_COMMIT_SUMMARY.md           # Git 提交总结
    ├── LANGCHAIN_INTEGRATION_SUMMARY.md # LangChain 集成总结
    ├── LANGCHAIN_COMPLETION_REPORT.md  # LangChain 完成报告
    ├── AGENT_VERIFICATION_SUMMARY.md   # 智能代理验证总结
    └── INCREMENTAL_ANALYSIS_IMPLEMENTATION.md # 增量分析实现总结 ⚡⭐
```

## 📖 使用指南 (guides/)

### 核心功能指南

- **[DIRECTORY_SCANNER_GUIDE.md](guides/DIRECTORY_SCANNER_GUIDE.md)**
  - 目录扫描器的详细使用说明
  - 支持的编程语言
  - 命令行参数
  - 使用示例

- **[LANGCHAIN_AGENT_GUIDE.md](guides/LANGCHAIN_AGENT_GUIDE.md)**
  - LangChain 智能代理完整指南
  - 架构设计说明
  - 工具集介绍
  - API 使用方法
  - 故障排除

- **[AGENT_VERIFICATION_GUIDE.md](guides/AGENT_VERIFICATION_GUIDE.md)**
  - 智能代理验证步骤
  - 手动测试方法
  - 常见问题解决

- **[INCREMENTAL_ANALYSIS_GUIDE.md](guides/INCREMENTAL_ANALYSIS_GUIDE.md)** ⚡⭐
  - 增量代码分析完整指南
  - 智能变更检测机制
  - 缓存管理和优化
  - 使用场景和最佳实践
  - API 参考文档

- **[INCREMENTAL_ANALYSIS_QUICKREF.md](guides/INCREMENTAL_ANALYSIS_QUICKREF.md)** ⚡
  - 增量分析快速参考卡
  - 常用命令速查
  - 使用场景示例
  - 故障排除快速指南

- **[KNOWLEDGE_GRAPH_BUILDER_GUIDE.md](guides/KNOWLEDGE_GRAPH_BUILDER_GUIDE.md)** 📊⭐
  - 代码知识图谱构建完整指南
  - 图谱结构和节点类型
  - Cypher 查询示例
  - 可视化和分析方法
  - API 参考和最佳实践

### 快速开始

- **[QUICKSTART_LANGCHAIN.md](guides/QUICKSTART_LANGCHAIN.md)**
  - 5 分钟快速上手 LangChain 智能代理
  - 基本使用场景
  - 常见问题

### 部署指南

- **[DOCKER_DEPLOY.md](guides/DOCKER_DEPLOY.md)**
  - Docker 容器化部署
  - docker-compose 配置
  - 服务管理

- **[NEO4J_GUIDE.md](guides/NEO4J_GUIDE.md)**
  - Neo4j 图数据库使用
  - 代码知识图谱
  - 查询示例

## 📊 项目报告 (reports/)

### 项目总结

- **[PROJECT_SUMMARY.md](reports/PROJECT_SUMMARY.md)**
  - 项目整体概述
  - 功能特性
  - 技术栈

### 开发报告

- **[GIT_COMMIT_SUMMARY.md](reports/GIT_COMMIT_SUMMARY.md)**
  - Git 提交历史总结
  - 功能开发记录

- **[LANGCHAIN_INTEGRATION_SUMMARY.md](reports/LANGCHAIN_INTEGRATION_SUMMARY.md)**
  - LangChain 集成技术总结
  - 架构设计
  - 性能对比
  - 未来规划

- **[LANGCHAIN_COMPLETION_REPORT.md](reports/LANGCHAIN_COMPLETION_REPORT.md)**
  - LangChain 集成完成报告
  - 交付内容
  - 验证结果

- **[AGENT_VERIFICATION_SUMMARY.md](reports/AGENT_VERIFICATION_SUMMARY.md)**
  - 智能代理验证总结
  - 功能测试结果
  - 使用建议

- **[INCREMENTAL_ANALYSIS_IMPLEMENTATION.md](reports/INCREMENTAL_ANALYSIS_IMPLEMENTATION.md)** ⚡⭐
  - 增量代码分析实现总结
  - 核心功能特性
  - 技术实现细节
  - 性能优化效果
  - 后续优化建议

## 🚀 快速导航

### 新手入门
1. 阅读 [README.md](../README.md) 了解项目概况
2. 查看 [QUICKSTART_LANGCHAIN.md](guides/QUICKSTART_LANGCHAIN.md) 快速上手
3. 参考 [DOCKER_DEPLOY.md](guides/DOCKER_DEPLOY.md) 部署项目

### 功能使用
- 代码扫描: [DIRECTORY_SCANNER_GUIDE.md](guides/DIRECTORY_SCANNER_GUIDE.md)
- 智能分析: [LANGCHAIN_AGENT_GUIDE.md](guides/LANGCHAIN_AGENT_GUIDE.md)
- 增量分析: [INCREMENTAL_ANALYSIS_GUIDE.md](guides/INCREMENTAL_ANALYSIS_GUIDE.md) ⚡⭐
- 知识图谱: [KNOWLEDGE_GRAPH_BUILDER_GUIDE.md](guides/KNOWLEDGE_GRAPH_BUILDER_GUIDE.md) 📊⭐
- 图数据库: [NEO4J_GUIDE.md](guides/NEO4J_GUIDE.md)

### 技术深入
- 架构设计: [LANGCHAIN_INTEGRATION_SUMMARY.md](reports/LANGCHAIN_INTEGRATION_SUMMARY.md)
- 项目总结: [PROJECT_SUMMARY.md](reports/PROJECT_SUMMARY.md)

## 📝 文档维护

### 更新指南

当添加新功能或修改现有功能时，请更新相应的文档：

1. **新增功能** - 在 `guides/` 创建新的指南文档
2. **功能修改** - 更新对应的指南文档
3. **项目里程碑** - 在 `reports/` 添加总结报告

### 文档规范

- 使用 Markdown 格式
- 包含清晰的标题和目录
- 提供代码示例
- 添加使用场景说明
- 包含故障排除部分

## 🔗 相关链接

- [项目主页](../README.md)
- [API 文档](../api/API_DOCS.md)
- [测试文档](../tests/README.md)

---

**最后更新**: 2025-12-07
