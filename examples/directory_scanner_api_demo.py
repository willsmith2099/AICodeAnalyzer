#!/usr/bin/env python3
"""
Directory Scanner Python API 使用示例
展示如何在 Python 代码中使用 Directory Scanner
"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from directory_scanner import DirectoryScanner


def example_1_basic_usage():
    """示例 1: 基本用法"""
    print("=" * 80)
    print("示例 1: 基本用法")
    print("=" * 80)
    
    scanner = DirectoryScanner(
        root_dir="../examples",
        output_dir="../example_reports/basic",
        extensions=['.java']
    )
    
    files = scanner.scan_directory()
    print(f"\n找到 {len(files)} 个文件")


def example_2_remote_ollama():
    """示例 2: 使用远程 Ollama"""
    print("\n" + "=" * 80)
    print("示例 2: 使用远程 Ollama")
    print("=" * 80)
    
    scanner = DirectoryScanner(
        root_dir="../examples",
        output_dir="../example_reports/remote",
        extensions=['.java'],
        ollama_url="http://192.168.1.100:11434",  # 远程地址
        model="qwen2.5:7b"  # 使用更大的模型
    )
    
    print(f"配置的 Ollama 地址: {scanner.ollama_url}")
    print(f"配置的模型: {scanner.model}")


def example_3_regex_filter():
    """示例 3: 使用正则表达式过滤"""
    print("\n" + "=" * 80)
    print("示例 3: 使用正则表达式过滤")
    print("=" * 80)
    
    scanner = DirectoryScanner(
        root_dir="../examples",
        output_dir="../example_reports/filtered",
        extensions=['.java'],
        file_pattern=".*Test.*"  # 只分析包含 Test 的文件
    )
    
    files = scanner.scan_directory()
    print(f"\n找到 {len(files)} 个匹配的文件")


def example_4_call_chain_analysis():
    """示例 4: 启用调用链分析"""
    print("\n" + "=" * 80)
    print("示例 4: 启用调用链分析")
    print("=" * 80)
    
    scanner = DirectoryScanner(
        root_dir="../examples",
        output_dir="../example_reports/callchain",
        extensions=['.java'],
        enable_call_chain=True  # 启用调用链分析
    )
    
    files = scanner.scan_directory()
    if files:
        print(f"\n正在分析第一个文件: {files[0]}")
        result = scanner.analyze_file(files[0])
        
        if result.get('call_chain'):
            call_chain = result['call_chain']
            print(f"\n调用链统计:")
            print(f"  - 函数数量: {len(call_chain.get('functions', []))}")
            print(f"  - 调用关系数: {sum(len(v) for v in call_chain.get('call_graph', {}).values())}")


def example_5_comprehensive():
    """示例 5: 完整功能组合"""
    print("\n" + "=" * 80)
    print("示例 5: 完整功能组合")
    print("=" * 80)
    
    scanner = DirectoryScanner(
        root_dir="../examples",
        output_dir="../example_reports/comprehensive",
        extensions=['.java'],
        ollama_url="http://localhost:11434",
        model="qwen2.5:0.5b",
        file_pattern=".*",  # 所有文件
        enable_call_chain=True  # 启用调用链
    )
    
    print("\n配置信息:")
    print(f"  - Ollama URL: {scanner.ollama_url}")
    print(f"  - 模型: {scanner.model}")
    print(f"  - 调用链分析: {'启用' if scanner.enable_call_chain else '禁用'}")
    
    files = scanner.scan_directory()
    print(f"\n找到 {len(files)} 个文件")


def example_6_batch_analysis():
    """示例 6: 批量分析多个目录"""
    print("\n" + "=" * 80)
    print("示例 6: 批量分析多个目录")
    print("=" * 80)
    
    directories = [
        "../examples",
        "../src",
        "../tests"
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"\n正在扫描: {directory}")
            scanner = DirectoryScanner(
                root_dir=directory,
                extensions=['.py', '.java'],
                file_pattern=".*demo.*"
            )
            files = scanner.scan_directory()
            print(f"  找到 {len(files)} 个文件")


def example_7_custom_analysis():
    """示例 7: 自定义分析流程"""
    print("\n" + "=" * 80)
    print("示例 7: 自定义分析流程")
    print("=" * 80)
    
    scanner = DirectoryScanner(
        root_dir="../examples",
        extensions=['.java'],
        enable_call_chain=True
    )
    
    # 只扫描，不分析
    files = scanner.scan_directory()
    
    # 手动选择要分析的文件
    if files:
        print(f"\n找到 {len(files)} 个文件，选择第一个进行分析")
        result = scanner.analyze_file(files[0])
        
        print(f"\n分析结果:")
        print(f"  - 状态: {result['status']}")
        print(f"  - 文件: {result['file_path']}")
        print(f"  - 语言: {result['language']}")
        
        if result.get('call_chain'):
            print(f"  - 函数数量: {len(result['call_chain']['functions'])}")


def example_8_error_handling():
    """示例 8: 错误处理"""
    print("\n" + "=" * 80)
    print("示例 8: 错误处理")
    print("=" * 80)
    
    try:
        scanner = DirectoryScanner(
            root_dir="/nonexistent/path",
            extensions=['.java']
        )
    except ValueError as e:
        print(f"捕获到预期的错误: {e}")
    
    # 正确的用法
    scanner = DirectoryScanner(
        root_dir="../examples",
        extensions=['.java']
    )
    print("✓ 扫描器创建成功")


def main():
    """运行所有示例"""
    print("Directory Scanner Python API 使用示例")
    print("=" * 80)
    
    # 运行示例（注释掉不需要的）
    example_1_basic_usage()
    example_2_remote_ollama()
    example_3_regex_filter()
    # example_4_call_chain_analysis()  # 需要 Ollama 运行
    example_5_comprehensive()
    example_6_batch_analysis()
    example_7_custom_analysis()
    example_8_error_handling()
    
    print("\n" + "=" * 80)
    print("所有示例运行完成！")
    print("=" * 80)


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    main()
