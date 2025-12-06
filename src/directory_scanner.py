#!/usr/bin/env python3
"""
Directory Scanner - 递归扫描目录下的程序文件并使用 Ollama 进行分析
"""

import os
import sys
from typing import List, Dict, Set
import json
from datetime import datetime

# Add the src directory to the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm.ollama_client import OllamaClient


class DirectoryScanner:
    """扫描目录并分析程序文件的工具类"""
    
    # 支持的编程语言及其文件扩展名
    SUPPORTED_EXTENSIONS = {
        '.py': 'Python', '.java': 'Java', '.js': 'JavaScript', '.ts': 'TypeScript',
        '.jsx': 'React JSX', '.tsx': 'React TSX', '.cpp': 'C++', '.cc': 'C++',
        '.cxx': 'C++', '.c': 'C', '.h': 'C/C++ Header', '.hpp': 'C++ Header',
        '.cs': 'C#', '.go': 'Go', '.rs': 'Rust', '.rb': 'Ruby', '.php': 'PHP',
        '.swift': 'Swift', '.kt': 'Kotlin', '.scala': 'Scala', '.r': 'R',
        '.m': 'Objective-C', '.sh': 'Shell', '.bash': 'Bash', '.sql': 'SQL',
        '.pl': 'Perl', '.lua': 'Lua', '.dart': 'Dart', '.vue': 'Vue',
    }
    
    DEFAULT_IGNORE_DIRS = {
        '.git', '.svn', '.hg', 'node_modules', '__pycache__', '.venv', 'venv',
        'build', 'dist', 'target', 'out', '.idea', '.vscode', '.vs', 'vendor', 'packages',
    }
    
    def __init__(self, root_dir: str, output_dir: str = None, extensions: List[str] = None,
                 ignore_dirs: Set[str] = None, max_file_size: int = 1024 * 1024):
        self.root_dir = os.path.abspath(root_dir)
        self.output_dir = output_dir
        self.extensions = extensions or list(self.SUPPORTED_EXTENSIONS.keys())
        self.ignore_dirs = ignore_dirs or self.DEFAULT_IGNORE_DIRS
        self.max_file_size = max_file_size
        
        if not os.path.isdir(self.root_dir):
            raise ValueError(f"目录不存在: {self.root_dir}")
        
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
            print(f"✓ 报告将保存到: {self.output_dir}\n")
        
        self.ollama_client = OllamaClient()
        self.stats = {'total_files': 0, 'analyzed_files': 0, 'skipped_files': 0, 'failed_files': 0, 'total_size': 0}
    
    def scan_directory(self) -> List[str]:
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
    
    def get_analysis_prompt(self, file_path: str, content: str, language: str) -> str:
        return f"""请分析以下 {language} 代码文件并提供详细的分析报告。

文件路径: {file_path}
编程语言: {language}

代码内容:
```{language.lower()}
{content}
```

请从以下几个方面进行分析：

1. **代码概述** - 文件的主要功能和用途，核心类、函数或模块的说明
2. **代码质量** - 代码结构和组织、命名规范、注释完整性、代码复杂度评估
3. **潜在问题** - 可能的 bug 或逻辑错误、性能问题、安全隐患、代码异味
4. **改进建议** - 重构建议、性能优化建议、最佳实践建议、可维护性改进
5. **依赖关系** - 导入的库和模块、外部依赖

请以 Markdown 格式输出分析报告，使用清晰的标题和列表。"""
    
    def analyze_file(self, file_path: str) -> Dict:
        rel_path = os.path.relpath(file_path, self.root_dir)
        file_ext = os.path.splitext(file_path)[1].lower()
        language = self.SUPPORTED_EXTENSIONS.get(file_ext, 'Unknown')
        
        result = {'file_path': rel_path, 'language': language, 'status': 'pending', 'analysis': None, 'error': None}
        
        print(f"{'='*80}")
        print(f"📄 分析文件: {rel_path}")
        print(f"🔤 语言: {language}")
        print(f"{'='*80}\n")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            prompt = self.get_analysis_prompt(rel_path, content, language)
            print("🤖 正在调用 Ollama 进行分析...")
            analysis = self.ollama_client.generate_response(prompt)
            
            result['status'] = 'success'
            result['analysis'] = analysis
            self.stats['analyzed_files'] += 1
            
            print("\n" + "="*80)
            print("📊 分析结果")
            print("="*80)
            print(analysis)
            print("\n")
            
            if self.output_dir:
                self._save_analysis(rel_path, language, analysis)
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            self.stats['failed_files'] += 1
            print(f"❌ 分析失败: {e}\n")
        
        return result
    
    def _save_analysis(self, file_path: str, language: str, analysis: str):
        safe_path = file_path.replace(os.sep, '_').replace('.', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(self.output_dir, f"{safe_path}_analysis_{timestamp}.md")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 代码分析报告\n\n")
            f.write(f"**文件路径**: `{file_path}`\n\n")
            f.write(f"**编程语言**: {language}\n\n")
            f.write(f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(analysis)
        
        print(f"✓ 分析报告已保存: {output_file}\n")
    
    def analyze_all(self) -> List[Dict]:
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
        print("\n" + "="*80)
        print("📈 分析统计")
        print("="*80)
        print(f"扫描的文件总数: {self.stats['total_files']}")
        print(f"成功分析: {self.stats['analyzed_files']}")
        print(f"跳过的文件: {self.stats['skipped_files']}")
        print(f"失败的文件: {self.stats['failed_files']}")
        print(f"总文件大小: {self.stats['total_size'] / 1024:.2f} KB")
        print("="*80)
    
    def _save_summary(self, results: List[Dict]):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = os.path.join(self.output_dir, f"summary_{timestamp}.md")
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# 代码分析汇总报告\n\n")
            f.write(f"**扫描目录**: `{self.root_dir}`\n\n")
            f.write(f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 统计信息\n\n")
            f.write(f"- 扫描的文件总数: {self.stats['total_files']}\n")
            f.write(f"- 成功分析: {self.stats['analyzed_files']}\n")
            f.write(f"- 跳过的文件: {self.stats['skipped_files']}\n")
            f.write(f"- 失败的文件: {self.stats['failed_files']}\n")
            f.write(f"- 总文件大小: {self.stats['total_size'] / 1024:.2f} KB\n\n")
            f.write("## 分析结果\n\n")
            for result in results:
                status_emoji = "✅" if result['status'] == 'success' else "❌"
                f.write(f"{status_emoji} **{result['file_path']}** ({result['language']})\n")
                if result['error']:
                    f.write(f"   - 错误: {result['error']}\n")
                f.write("\n")
        
        print(f"\n✓ 汇总报告已保存: {summary_file}")
        
        json_file = os.path.join(self.output_dir, f"summary_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'root_dir': self.root_dir,
                'timestamp': datetime.now().isoformat(),
                'stats': self.stats,
                'results': results,
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✓ JSON 报告已保存: {json_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='递归扫描目录下的程序文件并使用 Ollama 进行分析')
    parser.add_argument('directory', help='要扫描的目录路径')
    parser.add_argument('-o', '--output', dest='output_dir', help='分析报告输出目录')
    parser.add_argument('-e', '--extensions', nargs='+', help='要扫描的文件扩展名（例如: .py .java .js）')
    parser.add_argument('--max-size', type=int, default=1024 * 1024, help='最大文件大小（字节），默认 1MB')
    parser.add_argument('--ignore-dirs', nargs='+', help='要忽略的目录名称')
    
    args = parser.parse_args()
    
    try:
        scanner = DirectoryScanner(
            root_dir=args.directory,
            output_dir=args.output_dir,
            extensions=args.extensions,
            ignore_dirs=set(args.ignore_dirs) if args.ignore_dirs else None,
            max_file_size=args.max_size
        )
        scanner.analyze_all()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
