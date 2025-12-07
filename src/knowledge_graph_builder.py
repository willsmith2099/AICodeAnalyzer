#!/usr/bin/env python3
"""
代码知识图谱构建器
扫描指定目录下的代码工程，提取代码结构并构建到 Neo4j 知识图谱中
"""

import os
import sys
from typing import List, Dict, Set, Optional
from pathlib import Path
from datetime import datetime
import json

# Add the src directory to the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graph.neo4j_client import Neo4jClient
from graph.code_parser import CodeParser


class KnowledgeGraphBuilder:
    """代码知识图谱构建器"""
    
    # 支持的编程语言及其文件扩展名
    SUPPORTED_EXTENSIONS = {
        '.java': 'Java',
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'React JSX',
        '.tsx': 'React TSX',
        '.cpp': 'C++',
        '.cc': 'C++',
        '.c': 'C',
        '.go': 'Go',
        '.rs': 'Rust',
    }
    
    DEFAULT_IGNORE_DIRS = {
        '.git', '.svn', '.hg', 'node_modules', '__pycache__', '.venv', 'venv',
        'build', 'dist', 'target', 'out', '.idea', '.vscode', '.vs', 'vendor',
        'packages', 'bin', 'obj', '.gradle', '.mvn'
    }
    
    def __init__(self, 
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j",
                 neo4j_password: str = "password",
                 extensions: List[str] = None,
                 ignore_dirs: Set[str] = None,
                 max_file_size: int = 1024 * 1024):
        """
        初始化知识图谱构建器
        
        Args:
            neo4j_uri: Neo4j 数据库连接 URI
            neo4j_user: Neo4j 用户名
            neo4j_password: Neo4j 密码
            extensions: 要扫描的文件扩展名列表
            ignore_dirs: 要忽略的目录集合
            max_file_size: 最大文件大小（字节）
        """
        # 初始化 Neo4j 客户端
        try:
            self.neo4j_client = Neo4jClient(neo4j_uri, neo4j_user, neo4j_password)
            print(f"✓ 成功连接到 Neo4j 数据库: {neo4j_uri}\n")
        except Exception as e:
            print(f"❌ 无法连接到 Neo4j 数据库: {e}")
            print("请确保 Neo4j 服务正在运行")
            raise
        
        # 初始化代码解析器
        self.parser = CodeParser(neo4j_client=self.neo4j_client)
        
        # 配置参数
        self.extensions = extensions or ['.java', '.py', '.js', '.ts']
        self.ignore_dirs = ignore_dirs or self.DEFAULT_IGNORE_DIRS
        self.max_file_size = max_file_size
        
        # 统计信息
        self.stats = {
            'total_files': 0,
            'parsed_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
            'total_classes': 0,
            'total_methods': 0,
            'total_size': 0
        }
    
    def scan_directory(self, root_dir: str) -> List[str]:
        """
        扫描目录，查找所有符合条件的代码文件
        
        Args:
            root_dir: 根目录路径
            
        Returns:
            文件路径列表
        """
        root_path = Path(root_dir).resolve()
        
        if not root_path.is_dir():
            raise ValueError(f"目录不存在: {root_dir}")
        
        print(f"🔍 开始扫描目录: {root_path}")
        print(f"📝 支持的文件类型: {', '.join(self.extensions)}\n")
        
        found_files = []
        
        for root, dirs, files in os.walk(root_path):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext not in self.extensions:
                    continue
                
                file_path = os.path.join(root, file)
                
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > self.max_file_size:
                        print(f"⚠️  跳过大文件 ({file_size / 1024:.1f} KB): {file_path}")
                        self.stats['skipped_files'] += 1
                        continue
                    
                    self.stats['total_size'] += file_size
                    found_files.append(file_path)
                    self.stats['total_files'] += 1
                    
                except OSError as e:
                    print(f"⚠️  无法访问文件: {file_path} - {e}")
        
        print(f"\n✓ 扫描完成，找到 {len(found_files)} 个文件")
        print(f"  总大小: {self.stats['total_size'] / 1024:.2f} KB\n")
        
        return found_files
    
    def build_graph(self, root_dir: str, clear_existing: bool = False) -> Dict:
        """
        构建代码知识图谱
        
        Args:
            root_dir: 项目根目录
            clear_existing: 是否清空现有图数据
            
        Returns:
            构建结果统计
        """
        print("="*80)
        print("🚀 代码知识图谱构建器")
        print("="*80)
        print(f"项目目录: {root_dir}")
        print("="*80 + "\n")
        
        # 清空现有图数据（如果需要）
        if clear_existing:
            print("🗑️  清空现有图数据...")
            self.neo4j_client.clear_graph()
            print("✓ 图数据已清空\n")
        
        # 创建索引
        print("📊 创建数据库索引...")
        self.neo4j_client.create_indexes()
        print("✓ 索引创建完成\n")
        
        # 扫描目录
        files = self.scan_directory(root_dir)
        
        if not files:
            print("⚠️  未找到符合条件的文件")
            return self.stats
        
        # 解析文件并构建图谱
        print("🔨 开始构建知识图谱...\n")
        
        for i, file_path in enumerate(files, 1):
            rel_path = os.path.relpath(file_path, root_dir)
            print(f"[{i}/{len(files)}] 解析: {rel_path}")
            
            try:
                # 解析文件
                structure = self.parser.parse_file(file_path)
                
                # 统计类和方法数量
                for class_info in structure.get('classes', []):
                    self.stats['total_classes'] += 1
                    self.stats['total_methods'] += len(class_info.get('methods', []))
                
                self.stats['parsed_files'] += 1
                print(f"  ✓ 成功 - 找到 {len(structure.get('classes', []))} 个类")
                
            except Exception as e:
                self.stats['failed_files'] += 1
                print(f"  ❌ 失败: {e}")
        
        # 打印统计信息
        self._print_summary()
        
        # 获取图数据库统计
        graph_stats = self.neo4j_client.get_statistics()
        
        return {
            'scan_stats': self.stats,
            'graph_stats': graph_stats
        }
    
    def _print_summary(self):
        """打印构建统计摘要"""
        print("\n" + "="*80)
        print("📊 构建统计")
        print("="*80)
        print(f"扫描的文件总数: {self.stats['total_files']}")
        print(f"成功解析: {self.stats['parsed_files']}")
        print(f"跳过的文件: {self.stats['skipped_files']}")
        print(f"失败的文件: {self.stats['failed_files']}")
        print(f"总文件大小: {self.stats['total_size'] / 1024:.2f} KB")
        print(f"提取的类: {self.stats['total_classes']}")
        print(f"提取的方法: {self.stats['total_methods']}")
        print("="*80)
    
    def export_graph_data(self, output_file: str):
        """
        导出图数据统计到 JSON 文件
        
        Args:
            output_file: 输出文件路径
        """
        graph_stats = self.neo4j_client.get_statistics()
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'scan_statistics': self.stats,
            'graph_statistics': graph_stats
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 图数据统计已导出到: {output_file}")
    
    def generate_report(self, output_file: str):
        """
        生成知识图谱构建报告
        
        Args:
            output_file: 输出文件路径
        """
        graph_stats = self.neo4j_client.get_statistics()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 代码知识图谱构建报告\n\n")
            f.write(f"**构建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 📊 扫描统计\n\n")
            f.write(f"- 扫描的文件总数: {self.stats['total_files']}\n")
            f.write(f"- 成功解析: {self.stats['parsed_files']}\n")
            f.write(f"- 跳过的文件: {self.stats['skipped_files']}\n")
            f.write(f"- 失败的文件: {self.stats['failed_files']}\n")
            f.write(f"- 总文件大小: {self.stats['total_size'] / 1024:.2f} KB\n")
            f.write(f"- 提取的类: {self.stats['total_classes']}\n")
            f.write(f"- 提取的方法: {self.stats['total_methods']}\n\n")
            
            f.write("## 🗄️ 图数据库统计\n\n")
            f.write(f"- 文件节点: {graph_stats.get('files', 0)}\n")
            f.write(f"- 类节点: {graph_stats.get('classes', 0)}\n")
            f.write(f"- 方法节点: {graph_stats.get('methods', 0)}\n")
            f.write(f"- 调用关系: {graph_stats.get('calls', 0)}\n")
            f.write(f"- 继承关系: {graph_stats.get('inheritance', 0)}\n\n")
            
            f.write("## 🔍 查询示例\n\n")
            f.write("### 查看所有类\n\n")
            f.write("```cypher\n")
            f.write("MATCH (c:Class) RETURN c.name, c.file_path LIMIT 10\n")
            f.write("```\n\n")
            
            f.write("### 查看类的方法\n\n")
            f.write("```cypher\n")
            f.write("MATCH (c:Class)-[:HAS_METHOD]->(m:Method)\n")
            f.write("RETURN c.name, collect(m.name) as methods\n")
            f.write("```\n\n")
            
            f.write("### 查看继承关系\n\n")
            f.write("```cypher\n")
            f.write("MATCH (child:Class)-[:EXTENDS]->(parent:Class)\n")
            f.write("RETURN child.name, parent.name\n")
            f.write("```\n\n")
            
            f.write("### 查看方法调用链\n\n")
            f.write("```cypher\n")
            f.write("MATCH (m1:Method)-[:CALLS]->(m2:Method)\n")
            f.write("RETURN m1.class_name + '.' + m1.name as caller,\n")
            f.write("       m2.class_name + '.' + m2.name as callee\n")
            f.write("```\n\n")
        
        print(f"✓ 构建报告已保存到: {output_file}")
    
    def close(self):
        """关闭数据库连接"""
        if self.neo4j_client:
            self.neo4j_client.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='代码知识图谱构建器 - 扫描代码工程并构建知识图谱',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 构建当前目录的知识图谱
  python3 src/knowledge_graph_builder.py . -o graph_report.md
  
  # 清空现有图数据并重新构建
  python3 src/knowledge_graph_builder.py . --clear
  
  # 只分析 Java 文件
  python3 src/knowledge_graph_builder.py . -e .java
  
  # 指定 Neo4j 连接参数
  python3 src/knowledge_graph_builder.py . --uri bolt://localhost:7687 --user neo4j --password mypassword
  
  # 导出图数据统计
  python3 src/knowledge_graph_builder.py . --export graph_stats.json
        """
    )
    
    parser.add_argument('directory', help='要扫描的项目目录')
    parser.add_argument('-o', '--output', dest='output_file', 
                       help='构建报告输出文件（Markdown 格式）')
    parser.add_argument('-e', '--extensions', nargs='+', 
                       help='要扫描的文件扩展名（例如: .py .java .js）')
    parser.add_argument('--clear', action='store_true', 
                       help='清空现有图数据')
    parser.add_argument('--uri', default='bolt://localhost:7687', 
                       help='Neo4j 连接 URI（默认: bolt://localhost:7687）')
    parser.add_argument('--user', default='neo4j', 
                       help='Neo4j 用户名（默认: neo4j）')
    parser.add_argument('--password', default='password', 
                       help='Neo4j 密码（默认: password）')
    parser.add_argument('--export', dest='export_file', 
                       help='导出图数据统计到 JSON 文件')
    parser.add_argument('--max-size', type=int, default=1024 * 1024, 
                       help='最大文件大小（字节），默认 1MB')
    
    args = parser.parse_args()
    
    try:
        # 创建构建器
        builder = KnowledgeGraphBuilder(
            neo4j_uri=args.uri,
            neo4j_user=args.user,
            neo4j_password=args.password,
            extensions=args.extensions,
            max_file_size=args.max_size
        )
        
        # 构建知识图谱
        results = builder.build_graph(args.directory, clear_existing=args.clear)
        
        # 生成报告
        if args.output_file:
            builder.generate_report(args.output_file)
        
        # 导出统计数据
        if args.export_file:
            builder.export_graph_data(args.export_file)
        
        # 关闭连接
        builder.close()
        
        print("\n✅ 知识图谱构建完成！")
        print(f"\n💡 提示:")
        print(f"  - 访问 Neo4j 浏览器: http://localhost:7474")
        print(f"  - 用户名: {args.user}")
        print(f"  - 密码: {args.password}")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
