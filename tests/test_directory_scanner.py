#!/usr/bin/env python3
"""
测试 Directory Scanner 的新功能
"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from directory_scanner import DirectoryScanner

def test_basic():
    """测试基本功能"""
    print("=" * 80)
    print("测试 1: 基本功能")
    print("=" * 80)
    
    scanner = DirectoryScanner(
        root_dir="../examples",
        extensions=['.java'],
        ollama_url="http://localhost:11434",
        model="qwen2.5:0.5b"
    )
    
    files = scanner.scan_directory()
    print(f"\n找到 {len(files)} 个文件")
    for f in files:
        print(f"  - {f}")

def test_file_pattern():
    """测试文件正则表达式过滤"""
    print("\n" + "=" * 80)
    print("测试 2: 文件正则表达式过滤（只匹配包含 'Test' 的文件）")
    print("=" * 80)
    
    scanner = DirectoryScanner(
        root_dir="../examples",
        extensions=['.java'],
        file_pattern=".*Test.*",
        ollama_url="http://localhost:11434",
        model="qwen2.5:0.5b"
    )
    
    files = scanner.scan_directory()
    print(f"\n找到 {len(files)} 个文件")
    for f in files:
        print(f"  - {f}")

def test_dir_pattern():
    """测试目录正则表达式过滤"""
    print("\n" + "=" * 80)
    print("测试 3: 目录正则表达式过滤（只扫描 'src' 目录）")
    print("=" * 80)
    
    scanner = DirectoryScanner(
        root_dir="..",
        extensions=['.py'],
        dir_pattern="^src$",
        ollama_url="http://localhost:11434",
        model="qwen2.5:0.5b"
    )
    
    files = scanner.scan_directory()
    print(f"\n找到 {len(files)} 个文件")
    print(f"前 5 个文件:")
    for f in files[:5]:
        print(f"  - {f}")

def test_remote_ollama():
    """测试远程 Ollama 配置"""
    print("\n" + "=" * 80)
    print("测试 4: 远程 Ollama 配置")
    print("=" * 80)
    
    scanner = DirectoryScanner(
        root_dir="../examples",
        extensions=['.java'],
        ollama_url="http://192.168.1.100:11434",  # 示例远程地址
        model="qwen2.5:7b"
    )
    
    print(f"配置的 Ollama 地址: {scanner.ollama_url}")
    print(f"配置的模型: {scanner.model}")

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    
    try:
        test_basic()
        test_file_pattern()
        test_dir_pattern()
        test_remote_ollama()
        
        print("\n" + "=" * 80)
        print("✅ 所有测试完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
