#!/bin/bash
# Directory Scanner 命令行使用示例
# 展示各种常用场景的命令行用法

echo "=================================="
echo "Directory Scanner 使用示例"
echo "=================================="
echo ""

# 示例 1: 基本用法
echo "示例 1: 基本用法 - 分析当前目录的 Java 文件"
echo "命令:"
echo "python src/directory_scanner.py . -e .java -o basic_reports"
echo ""

# 示例 2: 使用远程 Ollama
echo "示例 2: 使用远程 Ollama 服务"
echo "命令:"
echo "python src/directory_scanner.py /path/to/project \\"
echo "  --ollama-url http://192.168.1.100:11434 \\"
echo "  --model qwen2.5:7b \\"
echo "  -e .java \\"
echo "  -o remote_reports"
echo ""

# 示例 3: 使用正则表达式过滤
echo "示例 3: 使用正则表达式过滤 - 只分析 Service 类"
echo "命令:"
echo "python src/directory_scanner.py /path/to/project \\"
echo "  --file-pattern \".*Service.*\" \\"
echo "  -e .java \\"
echo "  -o service_reports"
echo ""

# 示例 4: 启用调用链分析
echo "示例 4: 启用调用链分析"
echo "命令:"
echo "python src/directory_scanner.py /path/to/project \\"
echo "  --enable-call-chain \\"
echo "  -e .java \\"
echo "  -o callchain_reports"
echo ""

# 示例 5: 完整功能组合
echo "示例 5: 完整功能组合 - 远程 Ollama + 正则过滤 + 调用链分析"
echo "命令:"
echo "python src/directory_scanner.py /path/to/project \\"
echo "  --ollama-url http://localhost:11434 \\"
echo "  --model qwen2.5:0.5b \\"
echo "  --file-pattern \".*Service.*\" \\"
echo "  --dir-pattern \"^(src|lib)$\" \\"
echo "  --enable-call-chain \\"
echo "  -e .java \\"
echo "  -o comprehensive_reports"
echo ""

# 示例 6: 分析 Python 项目
echo "示例 6: 分析 Python 项目"
echo "命令:"
echo "python src/directory_scanner.py ./src \\"
echo "  --file-pattern \".*analyzer.*\" \\"
echo "  --enable-call-chain \\"
echo "  -e .py \\"
echo "  -o python_reports"
echo ""

# 示例 7: 分析测试文件
echo "示例 7: 只分析测试文件"
echo "命令:"
echo "python src/directory_scanner.py ./tests \\"
echo "  --file-pattern \".*test.*\" \\"
echo "  -e .py .java \\"
echo "  -o test_reports"
echo ""

# 示例 8: 分析特定目录
echo "示例 8: 只分析 service 目录下的实现类"
echo "命令:"
echo "python src/directory_scanner.py /path/to/backend \\"
echo "  --dir-pattern \".*service.*\" \\"
echo "  --file-pattern \".*Impl.*\" \\"
echo "  --enable-call-chain \\"
echo "  -e .java \\"
echo "  -o service_impl_reports"
echo ""

# 示例 9: 限制文件大小
echo "示例 9: 限制文件大小 - 只分析小于 500KB 的文件"
echo "命令:"
echo "python src/directory_scanner.py /path/to/project \\"
echo "  --max-size 512000 \\"
echo "  -e .java \\"
echo "  -o small_files_reports"
echo ""

# 示例 10: 忽略特定目录
echo "示例 10: 忽略 test 和 build 目录"
echo "命令:"
echo "python src/directory_scanner.py /path/to/project \\"
echo "  --ignore-dirs test build target \\"
echo "  -e .java \\"
echo "  -o filtered_reports"
echo ""

echo "=================================="
echo "查看帮助信息"
echo "=================================="
echo "python src/directory_scanner.py --help"
echo ""

echo "=================================="
echo "实际运行示例 (取消注释以执行)"
echo "=================================="
echo ""

# 取消下面的注释以实际运行示例
# python src/directory_scanner.py examples --file-pattern ".*Test.*" --enable-call-chain -e .java -o example_reports
