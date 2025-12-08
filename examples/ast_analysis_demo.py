#!/usr/bin/env python3
"""
AST 静态分析和 Git 变更影响分析示例
"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ast_analyzer import ASTAnalyzer
from git_change_analyzer import GitChangeAnalyzer


def example_1_python_ast_analysis():
    """示例 1: Python AST 分析"""
    print("=" * 80)
    print("示例 1: Python AST 分析")
    print("=" * 80)
    
    analyzer = ASTAnalyzer(language='Python')
    
    # 分析 Python 文件
    result = analyzer.analyze_file('../src/ast_analyzer.py')
    
    print(f"\n文件: {result['file']}")
    print(f"类数量: {len(result.get('classes', []))}")
    print(f"函数数量: {len(result.get('functions', []))}")
    print(f"导入数量: {len(result.get('imports', []))}")
    
    if result.get('classes'):
        print("\n类列表:")
        for cls in result['classes'][:3]:
            print(f"  - {cls['name']} (第 {cls['line']} 行)")
            if cls.get('methods'):
                print(f"    方法: {', '.join(m['name'] for m in cls['methods'][:5])}")


def example_2_java_ast_analysis():
    """示例 2: Java AST 分析"""
    print("\n" + "=" * 80)
    print("示例 2: Java AST 分析")
    print("=" * 80)
    
    analyzer = ASTAnalyzer(language='Java')
    
    # 查找 Java 文件
    java_files = []
    for root, dirs, files in os.walk('../examples'):
        for file in files:
            if file.endswith('.java'):
                java_files.append(os.path.join(root, file))
    
    if java_files:
        result = analyzer.analyze_file(java_files[0])
        
        print(f"\n文件: {result['file']}")
        print(f"包名: {result.get('package', 'N/A')}")
        print(f"导入数量: {len(result.get('imports', []))}")
        print(f"类数量: {len(result.get('classes', []))}")
        
        if result.get('classes'):
            for cls in result['classes']:
                print(f"\n类: {cls['name']}")
                if cls.get('parent'):
                    print(f"  继承: {cls['parent']}")
                if cls.get('interfaces'):
                    print(f"  实现: {', '.join(cls['interfaces'])}")
                print(f"  方法数: {len(cls.get('methods', []))}")
    else:
        print("未找到 Java 文件")


def example_3_dependency_graph():
    """示例 3: 构建依赖关系图"""
    print("\n" + "=" * 80)
    print("示例 3: 构建依赖关系图")
    print("=" * 80)
    
    analyzer = ASTAnalyzer(language='Python')
    
    # 收集 Python 文件
    python_files = []
    for root, dirs, files in os.walk('../src'):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                python_files.append(os.path.join(root, file))
    
    if python_files[:5]:  # 只分析前5个文件
        print(f"\n分析 {len(python_files[:5])} 个文件...")
        dependency_graph = analyzer.build_dependency_graph(python_files[:5])
        
        print(f"\n依赖关系:")
        for item, deps in list(dependency_graph['dependencies'].items())[:5]:
            if deps:
                print(f"  {os.path.basename(item)} -> {deps}")


def example_4_impact_analysis():
    """示例 4: 影响链分析"""
    print("\n" + "=" * 80)
    print("示例 4: 影响链分析")
    print("=" * 80)
    
    analyzer = ASTAnalyzer(language='Python')
    
    # 模拟变更项目
    changed_items = ['ast_analyzer.py::ASTAnalyzer']
    
    print(f"\n变更项目: {changed_items}")
    
    # 追踪影响
    impact = analyzer.trace_impact(changed_items, max_depth=3)
    
    print(f"\n受影响项目总数: {impact['total_affected']}")
    
    for item in changed_items:
        upstream = impact['upstream_impact'].get(item, [])
        if upstream:
            print(f"\n上游影响 (谁依赖 {item}):")
            for i, chain in enumerate(upstream[:3], 1):
                print(f"  {i}. {' ← '.join(chain)}")


def example_5_git_change_analysis():
    """示例 5: Git 变更分析"""
    print("\n" + "=" * 80)
    print("示例 5: Git 变更分析")
    print("=" * 80)
    
    try:
        analyzer = GitChangeAnalyzer('.', language='Python')
        
        # 获取最近的变更文件
        changed_files = analyzer.get_changed_files('HEAD~1..HEAD')
        
        print(f"\n最近变更的文件 ({len(changed_files)} 个):")
        for file in changed_files[:5]:
            print(f"  - {file}")
        
        if changed_files:
            # 获取第一个文件的详细变更
            diff_info = analyzer.get_file_diff(changed_files[0], 'HEAD~1..HEAD')
            print(f"\n文件: {diff_info['file']}")
            print(f"新增行数: {diff_info.get('added_lines', 0)}")
            print(f"删除行数: {diff_info.get('deleted_lines', 0)}")
            
    except Exception as e:
        print(f"Git 分析失败: {e}")
        print("(这是正常的，如果当前目录不是 Git 仓库)")


def example_6_full_impact_analysis():
    """示例 6: 完整的变更影响分析"""
    print("\n" + "=" * 80)
    print("示例 6: 完整的变更影响分析")
    print("=" * 80)
    
    try:
        analyzer = GitChangeAnalyzer('.', language='Python')
        
        print("\n正在分析最近的代码变更...")
        result = analyzer.analyze_change_impact('HEAD~1..HEAD', max_depth=3)
        
        print(f"\n{result['summary']}")
        
        # 生成报告
        report = analyzer.generate_report(result, '../change_impact_report.md')
        print("\n✓ 报告已生成: change_impact_report.md")
        
    except Exception as e:
        print(f"完整分析失败: {e}")
        print("(需要在 Git 仓库中运行)")


def main():
    """运行所有示例"""
    print("AST 静态分析和 Git 变更影响分析示例")
    print("=" * 80)
    
    os.chdir(os.path.dirname(__file__))
    
    # 运行示例
    example_1_python_ast_analysis()
    example_2_java_ast_analysis()
    example_3_dependency_graph()
    example_4_impact_analysis()
    example_5_git_change_analysis()
    # example_6_full_impact_analysis()  # 需要 Git 仓库
    
    print("\n" + "=" * 80)
    print("所有示例运行完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
