#!/usr/bin/env python3
"""
增量代码分析器示例
演示如何使用增量分析功能
"""

import sys
import os

# Add the src directory to the python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from incremental_analyzer import IncrementalAnalyzer


def example_basic_usage():
    """示例 1: 基本用法"""
    print("="*80)
    print("示例 1: 基本增量分析")
    print("="*80 + "\n")
    
    # 创建增量分析器
    analyzer = IncrementalAnalyzer(
        root_dir='../examples',  # 项目目录
        output_dir='incremental_reports',  # 输出目录
        extensions=['.java', '.py']  # 只分析 Java 和 Python 文件
    )
    
    # 执行增量分析
    results = analyzer.analyze_incremental()
    
    print(f"\n✓ 分析完成！共分析 {len(results)} 个文件")


def example_force_analysis():
    """示例 2: 强制分析所有文件"""
    print("\n" + "="*80)
    print("示例 2: 强制分析所有文件（忽略缓存）")
    print("="*80 + "\n")
    
    analyzer = IncrementalAnalyzer(
        root_dir='../examples',
        output_dir='incremental_reports'
    )
    
    # 强制分析所有文件
    results = analyzer.analyze_incremental(force_all=True)
    
    print(f"\n✓ 强制分析完成！共分析 {len(results)} 个文件")


def example_cache_management():
    """示例 3: 缓存管理"""
    print("\n" + "="*80)
    print("示例 3: 缓存管理")
    print("="*80 + "\n")
    
    analyzer = IncrementalAnalyzer(
        root_dir='../examples',
        output_dir='incremental_reports'
    )
    
    # 显示缓存信息
    print("查看缓存信息:")
    analyzer.show_cache_info()
    
    # 如果需要清空缓存
    # analyzer.clear_cache()


def example_git_mode():
    """示例 4: Git 模式 vs 哈希模式"""
    print("\n" + "="*80)
    print("示例 4: Git 模式 vs 哈希模式")
    print("="*80 + "\n")
    
    # Git 模式（默认）
    print("使用 Git 模式检测变更:")
    analyzer_git = IncrementalAnalyzer(
        root_dir='.',
        output_dir='incremental_reports',
        use_git=True
    )
    results_git = analyzer_git.analyze_incremental()
    
    print("\n" + "-"*80 + "\n")
    
    # 哈希模式
    print("使用文件哈希模式检测变更:")
    analyzer_hash = IncrementalAnalyzer(
        root_dir='.',
        output_dir='incremental_reports',
        use_git=False
    )
    results_hash = analyzer_hash.analyze_incremental()


def example_custom_cache_dir():
    """示例 5: 自定义缓存目录"""
    print("\n" + "="*80)
    print("示例 5: 自定义缓存目录")
    print("="*80 + "\n")
    
    analyzer = IncrementalAnalyzer(
        root_dir='../examples',
        output_dir='incremental_reports',
        cache_dir='.my_custom_cache'  # 自定义缓存目录
    )
    
    results = analyzer.analyze_incremental()
    
    print(f"\n✓ 分析完成！缓存保存在: .my_custom_cache")


def example_api_usage():
    """示例 6: API 编程方式使用"""
    print("\n" + "="*80)
    print("示例 6: API 编程方式使用")
    print("="*80 + "\n")
    
    from incremental_analyzer import IncrementalAnalyzer, AnalysisCache
    
    # 创建分析器
    analyzer = IncrementalAnalyzer(
        root_dir='../examples',
        output_dir='incremental_reports'
    )
    
    # 获取缓存统计
    cache_stats = analyzer.cache.get_statistics()
    print(f"缓存统计:")
    print(f"  - 已缓存文件数: {cache_stats['total_cached_files']}")
    print(f"  - 上次更新: {cache_stats['last_update']}")
    
    # 扫描并分类文件
    categorized = analyzer.scan_and_filter_files()
    print(f"\n文件分类:")
    print(f"  - 新文件: {len(categorized['new'])}")
    print(f"  - 已修改: {len(categorized['modified'])}")
    print(f"  - 未更改: {len(categorized['unchanged'])}")
    
    # 执行分析
    if categorized['new'] or categorized['modified']:
        results = analyzer.analyze_incremental()
        print(f"\n✓ 分析了 {len(results)} 个文件")
    else:
        print("\n✅ 没有需要分析的文件")


def main():
    """主函数"""
    print("\n🚀 增量代码分析器示例\n")
    
    # 运行示例
    try:
        # 示例 1: 基本用法
        example_basic_usage()
        
        # 示例 2: 强制分析
        # example_force_analysis()
        
        # 示例 3: 缓存管理
        example_cache_management()
        
        # 示例 4: Git 模式 vs 哈希模式
        # example_git_mode()
        
        # 示例 5: 自定义缓存目录
        # example_custom_cache_dir()
        
        # 示例 6: API 编程方式
        example_api_usage()
        
        print("\n" + "="*80)
        print("✅ 所有示例运行完成！")
        print("="*80 + "\n")
        
        print("💡 提示:")
        print("  - 取消注释其他示例函数来运行更多示例")
        print("  - 查看生成的报告文件了解详细分析结果")
        print("  - 修改 examples 目录下的文件，然后再次运行查看增量分析效果")
        print()
        
    except Exception as e:
        print(f"\n❌ 运行示例时出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
