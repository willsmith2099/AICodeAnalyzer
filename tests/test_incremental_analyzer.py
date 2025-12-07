#!/usr/bin/env python3
"""
增量代码分析器测试脚本
演示增量分析功能的使用
"""

import os
import sys
import time
import shutil
from pathlib import Path

# Add the src directory to the python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from incremental_analyzer import IncrementalAnalyzer


def print_section(title):
    """打印分节标题"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_incremental_analysis():
    """测试增量代码分析功能"""
    
    # 设置测试目录
    test_dir = Path(__file__).parent.parent / "examples"
    output_dir = Path(__file__).parent.parent / "test_incremental_reports"
    
    # 清理之前的测试结果
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    print_section("增量代码分析器测试")
    
    print(f"📁 测试目录: {test_dir}")
    print(f"📁 输出目录: {output_dir}")
    print()
    
    # ========================================================================
    # 测试 1: 首次运行 - 所有文件都是新文件
    # ========================================================================
    print_section("测试 1: 首次运行（所有文件都是新文件）")
    
    analyzer = IncrementalAnalyzer(
        root_dir=str(test_dir),
        output_dir=str(output_dir),
        extensions=['.java']  # 只分析 Java 文件
    )
    
    print("执行首次增量分析...\n")
    results1 = analyzer.analyze_incremental(verbose=True)
    
    print(f"\n✓ 首次分析完成，分析了 {len(results1)} 个文件")
    
    # 等待一下
    time.sleep(2)
    
    # ========================================================================
    # 测试 2: 再次运行 - 没有文件更改
    # ========================================================================
    print_section("测试 2: 再次运行（没有文件更改）")
    
    analyzer2 = IncrementalAnalyzer(
        root_dir=str(test_dir),
        output_dir=str(output_dir),
        extensions=['.java']
    )
    
    print("执行第二次增量分析...\n")
    results2 = analyzer2.analyze_incremental(verbose=True)
    
    print(f"\n✓ 第二次分析完成，分析了 {len(results2)} 个文件")
    print("✅ 预期结果：0 个文件（因为没有文件更改）")
    
    # ========================================================================
    # 测试 3: 查看缓存信息
    # ========================================================================
    print_section("测试 3: 查看缓存信息")
    
    analyzer2.show_cache_info()
    
    # ========================================================================
    # 测试 4: 强制分析所有文件
    # ========================================================================
    print_section("测试 4: 强制分析所有文件（忽略缓存）")
    
    analyzer3 = IncrementalAnalyzer(
        root_dir=str(test_dir),
        output_dir=str(output_dir),
        extensions=['.java']
    )
    
    print("执行强制全量分析...\n")
    results3 = analyzer3.analyze_incremental(force_all=True, verbose=True)
    
    print(f"\n✓ 强制分析完成，分析了 {len(results3)} 个文件")
    
    # ========================================================================
    # 测试 5: 模拟文件修改
    # ========================================================================
    print_section("测试 5: 模拟文件修改")
    
    # 创建一个临时测试文件
    test_file = test_dir / "TempTest.java"
    print(f"创建临时测试文件: {test_file}")
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("""
public class TempTest {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
""")
    
    try:
        analyzer4 = IncrementalAnalyzer(
            root_dir=str(test_dir),
            output_dir=str(output_dir),
            extensions=['.java']
        )
        
        print("\n执行增量分析（应该检测到新文件）...\n")
        results4 = analyzer4.analyze_incremental(verbose=True)
        
        print(f"\n✓ 分析完成，分析了 {len(results4)} 个文件")
        print("✅ 预期结果：1 个文件（新增的 TempTest.java）")
        
        # 修改文件
        time.sleep(1)
        print("\n修改临时测试文件...")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""
public class TempTest {
    public static void main(String[] args) {
        System.out.println("Hello, Modified World!");
        System.out.println("This is a modification!");
    }
}
""")
        
        analyzer5 = IncrementalAnalyzer(
            root_dir=str(test_dir),
            output_dir=str(output_dir),
            extensions=['.java'],
            use_git=False  # 使用文件哈希模式
        )
        
        print("\n执行增量分析（应该检测到文件修改）...\n")
        results5 = analyzer5.analyze_incremental(verbose=True)
        
        print(f"\n✓ 分析完成，分析了 {len(results5)} 个文件")
        print("✅ 预期结果：1 个文件（修改的 TempTest.java）")
        
    finally:
        # 清理临时文件
        if test_file.exists():
            test_file.unlink()
            print(f"\n✓ 已删除临时测试文件: {test_file}")
    
    # ========================================================================
    # 测试总结
    # ========================================================================
    print_section("测试总结")
    
    print("✅ 所有测试完成！\n")
    print("测试内容:")
    print("  1. ✓ 首次运行 - 所有文件都被分析")
    print("  2. ✓ 再次运行 - 没有文件被分析（缓存生效）")
    print("  3. ✓ 查看缓存信息")
    print("  4. ✓ 强制分析 - 忽略缓存分析所有文件")
    print("  5. ✓ 文件修改检测 - 检测到新增和修改的文件")
    print()
    print(f"📊 生成的报告位置: {output_dir}")
    print(f"📦 缓存位置: {output_dir / '.cache'}")
    print()
    print("💡 提示:")
    print("  - 查看生成的报告文件了解详细分析结果")
    print("  - 查看缓存文件了解缓存机制")
    print("  - 尝试修改 examples 目录下的文件，然后再次运行测试")
    print()


def main():
    """主函数"""
    try:
        test_incremental_analysis()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
