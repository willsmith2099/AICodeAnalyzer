#!/usr/bin/env python3
"""
测试调用链分析功能
"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from directory_scanner import DirectoryScanner

def test_call_chain_analysis():
    """测试调用链分析功能"""
    print("=" * 80)
    print("测试: 调用链分析功能")
    print("=" * 80)
    
    # 使用 examples 目录中的 Java 文件进行测试
    scanner = DirectoryScanner(
        root_dir="../examples",
        output_dir="../test_call_chain_reports",
        extensions=['.java'],
        ollama_url="http://localhost:11434",
        model="qwen2.5:0.5b",
        enable_call_chain=True  # 启用调用链分析
    )
    
    files = scanner.scan_directory()
    print(f"\n找到 {len(files)} 个文件")
    
    if files:
        # 只分析第一个文件作为演示
        print(f"\n正在分析: {files[0]}")
        result = scanner.analyze_file(files[0])
        
        if result['status'] == 'success':
            print("\n✅ 分析成功！")
            
            if result.get('call_chain'):
                call_chain = result['call_chain']
                print(f"\n📊 调用链统计:")
                print(f"  - 函数数量: {len(call_chain.get('functions', []))}")
                print(f"  - 调用关系数: {sum(len(v) for v in call_chain.get('call_graph', {}).values())}")
                
                print(f"\n函数列表:")
                for func in call_chain.get('functions', [])[:5]:
                    print(f"  - {func['signature']}")
        else:
            print(f"\n❌ 分析失败: {result.get('error')}")

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    
    try:
        test_call_chain_analysis()
        
        print("\n" + "=" * 80)
        print("✅ 测试完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
