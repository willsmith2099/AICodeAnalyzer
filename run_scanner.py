#!/usr/bin/env python3
"""
运行目录扫描器并将所有输出保存到日志文件
"""

import subprocess
import sys
from datetime import datetime

# 日志文件
log_file = f"scanner_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

print(f"开始扫描 lingtools 项目...")
print(f"日志将保存到: {log_file}")
print("=" * 80)

# 运行命令
cmd = [
    sys.executable,
    "src/directory_scanner.py",
    "/Users/mac/Desktop/cursor/lingtools",
    "-o", "analysis_reports",
    "-e", ".java"
]

try:
    # 运行并捕获输出
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600  # 10分钟超时
    )
    
    # 保存到日志文件
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"命令: {' '.join(cmd)}\n")
        f.write(f"执行时间: {datetime.now()}\n")
        f.write("=" * 80 + "\n\n")
        f.write("STDOUT:\n")
        f.write(result.stdout)
        f.write("\n\nSTDERR:\n")
        f.write(result.stderr)
        f.write(f"\n\n返回码: {result.returncode}\n")
    
    # 显示结果
    print(f"\n✓ 扫描完成！")
    print(f"✓ 返回码: {result.returncode}")
    print(f"✓ 日志已保存: {log_file}")
    
    # 显示部分输出
    if result.stdout:
        print("\n输出预览:")
        print(result.stdout[:500])
    
    if result.stderr:
        print("\n错误信息:")
        print(result.stderr[:500])
    
    # 检查报告目录
    import os
    if os.path.exists('analysis_reports'):
        files = os.listdir('analysis_reports')
        print(f"\n✓ 生成了 {len(files)} 个报告文件")
        for f in files[:5]:
            print(f"  - {f}")
        if len(files) > 5:
            print(f"  ... 还有 {len(files) - 5} 个文件")
    else:
        print("\n⚠️  未找到 analysis_reports 目录")
    
except subprocess.TimeoutExpired:
    print("❌ 命令执行超时！")
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("命令执行超时\n")
        
except Exception as e:
    print(f"❌ 错误: {e}")
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"错误: {e}\n")
        import traceback
        f.write(traceback.format_exc())

print("\n" + "=" * 80)
print(f"完整日志请查看: {log_file}")
