#!/usr/bin/env python3
"""
代码知识图谱构建器示例
演示如何使用知识图谱构建器
"""

import sys
import os

# Add the src directory to the python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from knowledge_graph_builder import KnowledgeGraphBuilder
from graph.neo4j_client import Neo4jClient


def print_section(title):
    """打印分节标题"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def example_basic_usage():
    """示例 1: 基本用法"""
    print_section("示例 1: 基本知识图谱构建")
    
    try:
        # 创建构建器
        builder = KnowledgeGraphBuilder(
            neo4j_uri="bolt://localhost:7687",
            neo4j_user="neo4j",
            neo4j_password="password",
            extensions=['.java']  # 只分析 Java 文件
        )
        
        # 构建知识图谱
        results = builder.build_graph(
            root_dir='../examples',
            clear_existing=True  # 清空现有数据
        )
        
        # 生成报告
        builder.generate_report('graph_report.md')
        
        # 关闭连接
        builder.close()
        
        print("\n✓ 基本构建完成！")
        print(f"  - 报告文件: graph_report.md")
        
    except Exception as e:
        print(f"❌ 构建失败: {e}")


def example_query_graph():
    """示例 2: 查询知识图谱"""
    print_section("示例 2: 查询知识图谱")
    
    try:
        # 创建 Neo4j 客户端
        client = Neo4jClient(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password"
        )
        
        # 获取统计信息
        print("📊 图数据库统计:")
        stats = client.get_statistics()
        print(f"  - 文件节点: {stats.get('files', 0)}")
        print(f"  - 类节点: {stats.get('classes', 0)}")
        print(f"  - 方法节点: {stats.get('methods', 0)}")
        print(f"  - 调用关系: {stats.get('calls', 0)}")
        print(f"  - 继承关系: {stats.get('inheritance', 0)}")
        
        # 搜索方法
        print("\n🔍 搜索包含 'main' 的方法:")
        methods = client.search_methods_by_name('main')
        for method in methods[:5]:
            print(f"  - {method['class_name']}.{method['name']} ({method['file_path']}:{method['line_start']})")
        
        # 关闭连接
        client.close()
        
        print("\n✓ 查询完成！")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")


def example_incremental_build():
    """示例 3: 增量构建"""
    print_section("示例 3: 增量构建（不清空现有数据）")
    
    try:
        builder = KnowledgeGraphBuilder(
            extensions=['.java', '.py']
        )
        
        # 增量构建（不清空现有数据）
        results = builder.build_graph(
            root_dir='../examples',
            clear_existing=False  # 保留现有数据
        )
        
        # 导出统计数据
        builder.export_graph_data('graph_stats.json')
        
        builder.close()
        
        print("\n✓ 增量构建完成！")
        print(f"  - 统计文件: graph_stats.json")
        
    except Exception as e:
        print(f"❌ 构建失败: {e}")


def example_analyze_class():
    """示例 4: 分析特定类"""
    print_section("示例 4: 分析特定类的结构")
    
    try:
        client = Neo4jClient()
        
        # 假设我们要分析 'Application' 类
        class_name = 'Application'
        
        print(f"📋 分析类: {class_name}\n")
        
        # 获取类的所有方法
        print("方法列表:")
        methods = client.get_class_methods(class_name)
        for method in methods:
            params = ', '.join(method.get('parameters', []))
            print(f"  - {method['name']}({params}) -> {method.get('return_type', 'void')}")
            print(f"    位置: 第 {method['line_start']}-{method['line_end']} 行")
        
        # 获取类的继承层次
        print(f"\n继承层次:")
        hierarchy = client.get_class_hierarchy(class_name)
        if hierarchy['parents']:
            print(f"  父类: {', '.join(hierarchy['parents'])}")
        if hierarchy['children']:
            print(f"  子类: {', '.join(hierarchy['children'])}")
        if not hierarchy['parents'] and not hierarchy['children']:
            print(f"  （无继承关系）")
        
        client.close()
        
        print("\n✓ 分析完成！")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")


def example_export_and_visualize():
    """示例 5: 导出数据并提供可视化建议"""
    print_section("示例 5: 导出数据和可视化")
    
    try:
        builder = KnowledgeGraphBuilder()
        
        # 构建图谱
        results = builder.build_graph('../examples', clear_existing=True)
        
        # 导出统计数据
        builder.export_graph_data('graph_export.json')
        
        # 生成详细报告
        builder.generate_report('detailed_report.md')
        
        builder.close()
        
        print("\n✓ 导出完成！")
        print("\n📊 可视化建议:")
        print("  1. 访问 Neo4j 浏览器: http://localhost:7474")
        print("  2. 运行以下查询查看整体结构:")
        print()
        print("     MATCH (f:File)-[:CONTAINS]->(c:Class)-[:HAS_METHOD]->(m:Method)")
        print("     RETURN f, c, m")
        print("     LIMIT 50")
        print()
        print("  3. 查看继承关系图:")
        print()
        print("     MATCH path = (c1:Class)-[:EXTENDS]->(c2:Class)")
        print("     RETURN path")
        print()
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")


def main():
    """主函数"""
    print("\n🚀 代码知识图谱构建器示例\n")
    
    print("请确保 Neo4j 服务正在运行:")
    print("  docker-compose up -d neo4j")
    print()
    
    try:
        # 示例 1: 基本用法
        example_basic_usage()
        
        # 示例 2: 查询图谱
        example_query_graph()
        
        # 示例 3: 增量构建
        # example_incremental_build()
        
        # 示例 4: 分析特定类
        # example_analyze_class()
        
        # 示例 5: 导出和可视化
        # example_export_and_visualize()
        
        print("\n" + "="*80)
        print("✅ 所有示例运行完成！")
        print("="*80 + "\n")
        
        print("💡 提示:")
        print("  - 取消注释其他示例函数来运行更多示例")
        print("  - 查看生成的报告文件了解详细信息")
        print("  - 访问 Neo4j 浏览器进行可视化查询")
        print()
        
    except Exception as e:
        print(f"\n❌ 运行示例时出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
