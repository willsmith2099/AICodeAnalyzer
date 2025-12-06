#!/usr/bin/env python3
"""
智能目录扫描器 - 集成 LangChain Agent
使用智能代理进行更深入的代码分析
"""

import os
import sys
from typing import List, Dict, Set
import json
from datetime import datetime

# Add the src directory to the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.langchain_agent import CodeAnalysisAgent


class IntelligentDirectoryScanner:
    """智能目录扫描器 - 使用 LangChain Agent"""
    
    # 支持的编程语言及其文件扩展名
    SUPPORTED_EXTENSIONS = {
        '.py': 'Python', '.java': 'Java', '.js': 'JavaScript', '.ts': 'TypeScript',
        '.jsx': 'React JSX', '.tsx': 'React TSX', '.cpp': 'C++', '.cc': 'C++',
        '.cxx': 'C++', '.c': 'C', '.h': 'C/C++ Header', '.hpp': 'C++ Header',
        '.cs': 'C#', '.go': 'Go', '.rs': 'Rust', '.rb': 'Ruby', '.php': 'PHP',
        '.swift': 'Swift', '.kt': 'Kotlin', '.scala': 'Scala',
    }
    
    DEFAULT_IGNORE_DIRS = {
        '.git', '.svn', 'node_modules', '__pycache__', '.venv', 'venv',
        'build', 'dist', 'target', 'out', '.idea', '.vscode',
    }
    
    def __init__(self, root_dir: str, output_dir: str = None, extensions: List[str] = None,
                 ignore_dirs: Set[str] = None, max_file_size: int = 1024 * 1024,
                 use_agent: bool = True):
        """
        初始化智能目录扫描器
        
        Args:
            root_dir: 要扫描的根目录
            output_dir: 分析报告输出目录
            extensions: 要扫描的文件扩展名列表
            ignore_dirs: 要忽略的目录集合
            max_file_size: 最大文件大小（字节）
            use_agent: 是否使用 LangChain Agent（默认 True）
        """
        self.root_dir = os.path.abspath(root_dir)
        self.output_dir = output_dir
        self.extensions = extensions or list(self.SUPPORTED_EXTENSIONS.keys())
        self.ignore_dirs = ignore_dirs or self.DEFAULT_IGNORE_DIRS
        self.max_file_size = max_file_size
        self.use_agent = use_agent
        
        if not os.path.isdir(self.root_dir):
            raise ValueError(f"目录不存在: {self.root_dir}")
        
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
            print(f"✓ 报告将保存到: {self.output_dir}\n")
        
        # 初始化智能代理
        if self.use_agent:
            try:
                self.agent = CodeAnalysisAgent()
                print("✓ LangChain 智能代理已初始化\n")
            except Exception as e:
                print(f"⚠️  智能代理初始化失败: {e}")
                print("   将使用基础分析模式\n")
                self.use_agent = False
        
        self.stats = {
            'total_files': 0,
            'analyzed_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
            'total_size': 0,
        }
    
    def scan_directory(self) -> List[str]:
        """递归扫描目录，查找所有符合条件的程序文件"""
        found_files = []
        print(f"🔍 开始扫描目录: {self.root_dir}")
        print(f"📝 支持的文件类型: {', '.join(self.extensions)}\n")
        
        for root, dirs, files in os.walk(self.root_dir):
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
    
    def analyze_file_with_agent(self, file_path: str, content: str, language: str) -> Dict:
        """使用智能代理分析文件"""
        rel_path = os.path.relpath(file_path, self.root_dir)
        
        print(f"🤖 使用智能代理进行深度分析...")
        
        # 定义分析任务
        analysis_task = f"""
请对这个 {language} 代码文件进行全面的代码审查和分析。

文件: {rel_path}

请执行以下分析任务:
1. 分析代码质量（结构、命名、注释）
2. 检测潜在的 bug 和逻辑错误
3. 分析安全隐患
4. 提供改进建议
5. 提取依赖关系
6. 计算代码复杂度

请给出详细的分析报告。
"""
        
        try:
            # 使用智能代理的规划和执行功能
            result = self.agent.plan_and_execute(
                objective=analysis_task,
                context={
                    'file_path': rel_path,
                    'language': language,
                    'code': content,
                    'file_size': len(content)
                }
            )
            
            if result['status'] == 'success':
                return {
                    'status': 'success',
                    'analysis_type': 'agent',
                    'plan': result.get('plan', ''),
                    'analysis': result['execution_result'].get('result', ''),
                    'intermediate_steps': result['execution_result'].get('intermediate_steps', [])
                }
            else:
                return {
                    'status': 'error',
                    'analysis_type': 'agent',
                    'error': result.get('error', 'Unknown error')
                }
        except Exception as e:
            return {
                'status': 'error',
                'analysis_type': 'agent',
                'error': str(e)
            }
    
    def analyze_file(self, file_path: str) -> Dict:
        """分析单个文件"""
        rel_path = os.path.relpath(file_path, self.root_dir)
        file_ext = os.path.splitext(file_path)[1].lower()
        language = self.SUPPORTED_EXTENSIONS.get(file_ext, 'Unknown')
        
        result = {
            'file_path': rel_path,
            'language': language,
            'status': 'pending',
            'analysis': None,
            'error': None,
        }
        
        print(f"{'='*80}")
        print(f"📄 分析文件: {rel_path}")
        print(f"🔤 语言: {language}")
        print(f"{'='*80}\n")
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 使用智能代理分析
            if self.use_agent:
                analysis_result = self.analyze_file_with_agent(file_path, content, language)
                
                if analysis_result['status'] == 'success':
                    result['status'] = 'success'
                    result['analysis'] = analysis_result['analysis']
                    result['plan'] = analysis_result.get('plan', '')
                    result['analysis_type'] = 'agent'
                    self.stats['analyzed_files'] += 1
                    
                    # 显示分析结果
                    print("\n" + "="*80)
                    print("📊 智能代理分析结果")
                    print("="*80)
                    print("\n【分析计划】")
                    print(result['plan'])
                    print("\n【分析结果】")
                    print(result['analysis'])
                    print("\n")
                else:
                    raise Exception(analysis_result.get('error', 'Agent analysis failed'))
            else:
                # 基础分析模式
                result['status'] = 'success'
                result['analysis'] = f"基础分析: 文件包含 {len(content.split())} 个单词"
                result['analysis_type'] = 'basic'
                self.stats['analyzed_files'] += 1
            
            # 保存分析结果
            if self.output_dir:
                self._save_analysis(rel_path, language, result)
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            self.stats['failed_files'] += 1
            print(f"❌ 分析失败: {e}\n")
        
        return result
    
    def _save_analysis(self, file_path: str, language: str, result: Dict):
        """保存分析结果到文件"""
        safe_path = file_path.replace(os.sep, '_').replace('.', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(self.output_dir, f"{safe_path}_agent_analysis_{timestamp}.md")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 智能代码分析报告\n\n")
            f.write(f"**文件路径**: `{file_path}`\n\n")
            f.write(f"**编程语言**: {language}\n\n")
            f.write(f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**分析类型**: {result.get('analysis_type', 'unknown')}\n\n")
            f.write("---\n\n")
            
            if result.get('plan'):
                f.write("## 分析计划\n\n")
                f.write(result['plan'])
                f.write("\n\n")
            
            f.write("## 分析结果\n\n")
            f.write(result.get('analysis', ''))
        
        print(f"✓ 分析报告已保存: {output_file}\n")
    
    def analyze_all(self) -> List[Dict]:
        """分析所有扫描到的文件"""
        files = self.scan_directory()
        
        if not files:
            print("⚠️  未找到符合条件的文件")
            return []
        
        results = []
        for i, file_path in enumerate(files, 1):
            print(f"\n进度: [{i}/{len(files)}]")
            result = self.analyze_file(file_path)
            results.append(result)
        
        self._print_summary()
        
        if self.output_dir:
            self._save_summary(results)
        
        return results
    
    def _print_summary(self):
        """打印分析统计摘要"""
        print("\n" + "="*80)
        print("📈 分析统计")
        print("="*80)
        print(f"扫描的文件总数: {self.stats['total_files']}")
        print(f"成功分析: {self.stats['analyzed_files']}")
        print(f"跳过的文件: {self.stats['skipped_files']}")
        print(f"失败的文件: {self.stats['failed_files']}")
        print(f"总文件大小: {self.stats['total_size'] / 1024:.2f} KB")
        print(f"分析模式: {'智能代理' if self.use_agent else '基础模式'}")
        print("="*80)
    
    def _save_summary(self, results: List[Dict]):
        """保存汇总报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = os.path.join(self.output_dir, f"agent_summary_{timestamp}.md")
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# 智能代码分析汇总报告\n\n")
            f.write(f"**扫描目录**: `{self.root_dir}`\n\n")
            f.write(f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**分析模式**: {'LangChain 智能代理' if self.use_agent else '基础模式'}\n\n")
            f.write("## 统计信息\n\n")
            f.write(f"- 扫描的文件总数: {self.stats['total_files']}\n")
            f.write(f"- 成功分析: {self.stats['analyzed_files']}\n")
            f.write(f"- 跳过的文件: {self.stats['skipped_files']}\n")
            f.write(f"- 失败的文件: {self.stats['failed_files']}\n")
            f.write(f"- 总文件大小: {self.stats['total_size'] / 1024:.2f} KB\n\n")
            f.write("## 分析结果\n\n")
            
            for result in results:
                status_emoji = "✅" if result['status'] == 'success' else "❌"
                analysis_type = result.get('analysis_type', 'unknown')
                f.write(f"{status_emoji} **{result['file_path']}** ({result['language']}) - {analysis_type}\n")
                if result.get('error'):
                    f.write(f"   - 错误: {result['error']}\n")
                f.write("\n")
        
        print(f"\n✓ 汇总报告已保存: {summary_file}")
        
        # 保存 JSON 格式
        json_file = os.path.join(self.output_dir, f"agent_summary_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'root_dir': self.root_dir,
                'timestamp': datetime.now().isoformat(),
                'analysis_mode': 'agent' if self.use_agent else 'basic',
                'stats': self.stats,
                'results': results,
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✓ JSON 报告已保存: {json_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='智能目录扫描器 - 使用 LangChain Agent 进行深度分析')
    parser.add_argument('directory', help='要扫描的目录路径')
    parser.add_argument('-o', '--output', dest='output_dir', help='分析报告输出目录')
    parser.add_argument('-e', '--extensions', nargs='+', help='要扫描的文件扩展名')
    parser.add_argument('--max-size', type=int, default=1024 * 1024, help='最大文件大小（字节）')
    parser.add_argument('--ignore-dirs', nargs='+', help='要忽略的目录名称')
    parser.add_argument('--no-agent', action='store_true', help='禁用智能代理，使用基础分析')
    
    args = parser.parse_args()
    
    try:
        scanner = IntelligentDirectoryScanner(
            root_dir=args.directory,
            output_dir=args.output_dir,
            extensions=args.extensions,
            ignore_dirs=set(args.ignore_dirs) if args.ignore_dirs else None,
            max_file_size=args.max_size,
            use_agent=not args.no_agent
        )
        scanner.analyze_all()
        
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
