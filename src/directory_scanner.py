#!/usr/bin/env python3
"""
Directory Scanner - 递归扫描目录下的程序文件并使用 Ollama 进行分析
支持函数调用链分析和递归审核
"""

import os
import sys
import re
from typing import List, Dict, Set, Optional, Pattern
import json
from datetime import datetime

# Add the src directory to the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm.ollama_client import OllamaClient
from call_chain_analyzer import CallChainAnalyzer
from ast_analyzer import ASTAnalyzer


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
                 ignore_dirs: Set[str] = None, max_file_size: int = 1024 * 1024,
                 ollama_url: str = "http://localhost:11434", model: str = "qwen2.5:0.5b",
                 dir_pattern: Optional[str] = None, file_pattern: Optional[str] = None,
                 enable_call_chain: bool = False, enable_ast: bool = False):
        """
        初始化目录扫描器
        
        Args:
            root_dir: 要扫描的根目录
            output_dir: 分析报告输出目录
            extensions: 要扫描的文件扩展名列表
            ignore_dirs: 要忽略的目录名称集合
            max_file_size: 最大文件大小（字节）
            ollama_url: Ollama 服务地址
            model: 使用的模型名称
            dir_pattern: 目录名正则表达式（匹配的目录会被扫描）
            file_pattern: 文件名正则表达式（匹配的文件会被分析）
            enable_call_chain: 是否启用函数调用链分析
            enable_ast: 是否启用AST语法分析
        """
        self.root_dir = os.path.abspath(root_dir)
        self.output_dir = output_dir
        self.extensions = extensions or list(self.SUPPORTED_EXTENSIONS.keys())
        self.ignore_dirs = ignore_dirs or self.DEFAULT_IGNORE_DIRS
        self.max_file_size = max_file_size
        self.ollama_url = ollama_url
        self.model = model
        self.enable_call_chain = enable_call_chain
        self.enable_ast = enable_ast
        
        # 编译正则表达式
        self.dir_pattern: Optional[Pattern] = re.compile(dir_pattern) if dir_pattern else None
        self.file_pattern: Optional[Pattern] = re.compile(file_pattern) if file_pattern else None
        
        if not os.path.isdir(self.root_dir):
            raise ValueError(f"目录不存在: {self.root_dir}")
        
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
            print(f"✓ 报告将保存到: {self.output_dir}\n")
        
        # 使用配置的 Ollama 地址和模型
        self.ollama_client = OllamaClient(base_url=self.ollama_url, model=self.model)
        print(f"🤖 Ollama 配置:")
        print(f"   服务地址: {self.ollama_url}")
        print(f"   模型名称: {self.model}")
        
        if self.enable_call_chain:
            print(f"🔗 调用链分析: 已启用")
        if self.enable_ast:
            print(f"🔬 AST 语法分析: 已启用")
        if not self.enable_call_chain and not self.enable_ast:
            print()
        else:
            print()
        
        self.stats = {'total_files': 0, 'analyzed_files': 0, 'skipped_files': 0, 'failed_files': 0, 'total_size': 0}
    
    def _should_scan_directory(self, dir_name: str) -> bool:
        """判断是否应该扫描该目录"""
        # 如果在忽略列表中，不扫描
        if dir_name in self.ignore_dirs:
            return False
        
        # 如果设置了目录正则表达式，必须匹配
        if self.dir_pattern:
            return self.dir_pattern.search(dir_name) is not None
        
        return True
    
    def _should_analyze_file(self, file_name: str) -> bool:
        """判断是否应该分析该文件"""
        # 如果设置了文件正则表达式，必须匹配
        if self.file_pattern:
            return self.file_pattern.search(file_name) is not None
        
        return True
    
    def scan_directory(self) -> List[str]:
        found_files = []
        print(f"🔍 开始扫描目录: {self.root_dir}")
        print(f"📝 支持的文件类型: {', '.join(self.extensions)}")
        
        if self.dir_pattern:
            print(f"📁 目录过滤规则: {self.dir_pattern.pattern}")
        if self.file_pattern:
            print(f"📄 文件过滤规则: {self.file_pattern.pattern}")
        print()
        
        for root, dirs, files in os.walk(self.root_dir):
            # 过滤目录
            dirs[:] = [d for d in dirs if self._should_scan_directory(d)]
            
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext not in self.extensions:
                    continue
                
                # 检查文件名是否匹配正则表达式
                if not self._should_analyze_file(file):
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
        
        result = {
            'file_path': rel_path, 
            'language': language, 
            'status': 'pending', 
            'analysis': None, 
            'error': None,
            'call_chain': None
        }
        
        print(f"{'='*80}")
        print(f"📄 分析文件: {rel_path}")
        print(f"🔤 语言: {language}")
        print(f"{'='*80}\n")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 调用链分析
            call_chain_info = None
            if self.enable_call_chain:
                print("🔗 正在分析函数调用链...")
                call_chain_info = self._analyze_call_chain(content, file_path, language)
                result['call_chain'] = call_chain_info
                print(f"✓ 发现 {len(call_chain_info.get('functions', []))} 个函数\n")
            
            # AST 语法分析
            ast_info = None
            if self.enable_ast:
                print("🔬 正在进行 AST 语法分析...")
                ast_info = self._analyze_ast(content, file_path, language)
                result['ast_analysis'] = ast_info
                if ast_info:
                    print(f"✓ 提取了 {len(ast_info.get('classes', []))} 个类, {len(ast_info.get('functions', []))} 个函数\n")
            
            # 基础代码分析
            prompt = self.get_analysis_prompt(rel_path, content, language, call_chain_info, ast_info)
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
                self._save_analysis(rel_path, language, analysis, call_chain_info, ast_info)
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            self.stats['failed_files'] += 1
            print(f"❌ 分析失败: {e}\n")
        
        return result
    
    def _analyze_call_chain(self, content: str, file_path: str, language: str) -> Dict:
        """
        分析函数调用链
        
        Args:
            content: 文件内容
            file_path: 文件路径
            language: 编程语言
            
        Returns:
            调用链信息字典
        """
        analyzer = CallChainAnalyzer(language=language)
        call_graph = analyzer.build_call_graph(content, file_path)
        
        # 生成调用链报告
        call_chain_report = analyzer.generate_call_chain_report()
        mermaid_diagram = analyzer.generate_mermaid_diagram()
        
        return {
            'functions': call_graph['functions'],
            'call_graph': call_graph['call_graph'],
            'reverse_call_graph': call_graph['reverse_call_graph'],
            'report': call_chain_report,
            'mermaid': mermaid_diagram
        }
    
    def _analyze_ast(self, content: str, file_path: str, language: str) -> Optional[Dict]:
        """
        进行 AST 语法分析
        
        Args:
            content: 文件内容
            file_path: 文件路径
            language: 编程语言
            
        Returns:
            AST 分析信息字典
        """
        try:
            analyzer = ASTAnalyzer(language=language)
            ast_result = analyzer.analyze_file(file_path)
            
            # 构建依赖图（如果有多个文件可以传入）
            # dependency_graph = analyzer.build_dependency_graph([file_path])
            
            return {
                'classes': ast_result.get('classes', []),
                'functions': ast_result.get('functions', []),
                'imports': ast_result.get('imports', []),
                'calls': ast_result.get('calls', []),
                'package': ast_result.get('package'),
                'interfaces': ast_result.get('interfaces', [])
            }
        except Exception as e:
            print(f"⚠️  AST 分析失败: {e}")
            return None
    
    def get_analysis_prompt(self, file_path: str, content: str, language: str, 
                           call_chain_info: Optional[Dict] = None,
                           ast_info: Optional[Dict] = None) -> str:
        """生成分析提示词，包含调用链信息和AST信息"""
        
        base_prompt = f"""请分析以下 {language} 代码文件并提供详细的分析报告。

文件路径: {file_path}
编程语言: {language}

代码内容:
```{language.lower()}
{content}
```
"""
        
        # 如果有AST分析信息，添加到提示词中
        if ast_info:
            base_prompt += f"""

## AST 语法结构分析

"""
            if ast_info.get('package'):
                base_prompt += f"**包名**: `{ast_info['package']}`\n\n"
            
            if ast_info.get('classes'):
                base_prompt += f"**类定义** ({len(ast_info['classes'])} 个):\n"
                for cls in ast_info['classes'][:10]:
                    base_prompt += f"- `{cls['name']}`"
                    if cls.get('parent'):
                        base_prompt += f" extends `{cls['parent']}`"
                    if cls.get('interfaces'):
                        base_prompt += f" implements `{', '.join(cls['interfaces'])}`"
                    base_prompt += f" (第 {cls.get('line', 'N/A')} 行)\n"
                base_prompt += "\n"
            
            if ast_info.get('functions'):
                base_prompt += f"**函数定义** ({len(ast_info['functions'])} 个):\n"
                for func in ast_info['functions'][:10]:
                    base_prompt += f"- `{func['name']}` (第 {func.get('line', 'N/A')} 行)\n"
                base_prompt += "\n"
            
            if ast_info.get('imports'):
                base_prompt += f"**导入依赖** ({len(ast_info['imports'])} 个):\n"
                for imp in ast_info['imports'][:15]:
                    base_prompt += f"- `{imp}`\n"
                base_prompt += "\n"
        
        # 如果有调用链信息，添加到提示词中
        if call_chain_info and call_chain_info.get('functions'):
            base_prompt += f"""

## 函数调用链信息

该文件包含 {len(call_chain_info['functions'])} 个函数：
"""
            for func in call_chain_info['functions'][:10]:  # 只显示前10个
                base_prompt += f"- `{func['signature']}` (第 {func['start_line']}-{func['end_line']} 行)\n"
            
            if call_chain_info.get('call_graph'):
                base_prompt += "\n调用关系:\n"
                for caller, callees in list(call_chain_info['call_graph'].items())[:5]:
                    base_prompt += f"- `{caller}` 调用: {', '.join(f'`{c}`' for c in callees)}\n"
        
        base_prompt += """

请从以下几个方面进行分析：

1. **代码概述** - 文件的主要功能和用途，核心类、函数或模块的说明
2. **代码质量** - 代码结构和组织、命名规范、注释完整性、代码复杂度评估
3. **潜在问题** - 可能的 bug 或逻辑错误、性能问题、安全隐患、代码异味
4. **改进建议** - 重构建议、性能优化建议、最佳实践建议、可维护性改进
5. **依赖关系** - 导入的库和模块、外部依赖
"""
        
        if ast_info:
            base_prompt += """6. **AST 结构分析** - 基于上述 AST 信息，分析：
   - 类的设计和职责划分
   - 继承和接口实现的合理性
   - 依赖注入和解耦程度
   - 模块化程度
"""
        
        if call_chain_info:
            base_prompt += """7. **函数调用链分析** - 基于上述调用链信息，分析：
   - 关键函数的调用路径
   - 可能的循环调用或深度调用问题
   - 函数职责是否单一
   - 调用层次是否合理
"""
        
        base_prompt += "\n请以 Markdown 格式输出分析报告，使用清晰的标题和列表。"
        
        return base_prompt
    
    def _save_analysis(self, file_path: str, language: str, analysis: str, 
                      call_chain_info: Optional[Dict] = None, ast_info: Optional[Dict] = None):
        safe_path = file_path.replace(os.sep, '_').replace('.', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(self.output_dir, f"{safe_path}_analysis_{timestamp}.md")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 代码分析报告\n\n")
            f.write(f"**文件路径**: `{file_path}`\n\n")
            f.write(f"**编程语言**: {language}\n\n")
            f.write(f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 添加统计信息
            if call_chain_info:
                f.write(f"**函数数量**: {len(call_chain_info.get('functions', []))}\n\n")
            if ast_info:
                f.write(f"**类数量**: {len(ast_info.get('classes', []))}\n\n")
                f.write(f"**导入数量**: {len(ast_info.get('imports', []))}\n\n")
            
            f.write("---\n\n")
            
            # 如果有AST信息，先写入AST分析
            if ast_info:
                f.write("## 🔬 AST 语法结构分析\n\n")
                
                if ast_info.get('package'):
                    f.write(f"**包名**: `{ast_info['package']}`\n\n")
                
                if ast_info.get('classes'):
                    f.write(f"### 类定义 ({len(ast_info['classes'])} 个)\n\n")
                    for cls in ast_info['classes']:
                        f.write(f"#### `{cls['name']}`\n")
                        if cls.get('parent'):
                            f.write(f"- 继承: `{cls['parent']}`\n")
                        if cls.get('interfaces'):
                            f.write(f"- 实现接口: `{', '.join(cls['interfaces'])}`\n")
                        if cls.get('methods'):
                            f.write(f"- 方法数: {len(cls['methods'])}\n")
                        f.write("\n")
                
                if ast_info.get('imports'):
                    f.write(f"### 导入依赖 ({len(ast_info['imports'])} 个)\n\n")
                    for imp in ast_info['imports']:
                        f.write(f"- `{imp}`\n")
                    f.write("\n")
                
                f.write("---\n\n")
            
            # 如果有调用链信息，写入调用链报告
            if call_chain_info:
                f.write("## 📊 函数调用链分析\n\n")
                f.write(call_chain_info.get('report', ''))
                f.write("\n\n### 调用关系图\n\n")
                f.write(call_chain_info.get('mermaid', ''))
                f.write("\n\n---\n\n")
            
            # 写入代码分析结果
            f.write("## 🤖 AI 代码分析\n\n")
            f.write(analysis)
        
        print(f"✓ 分析报告已保存: {output_file}\n")
        
        # 如果有调用链信息，同时保存JSON格式
        if call_chain_info:
            json_file = os.path.join(self.output_dir, f"{safe_path}_callchain_{timestamp}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'file_path': file_path,
                    'language': language,
                    'timestamp': datetime.now().isoformat(),
                    'functions': call_chain_info.get('functions', []),
                    'call_graph': call_chain_info.get('call_graph', {}),
                    'reverse_call_graph': call_chain_info.get('reverse_call_graph', {})
                }, f, ensure_ascii=False, indent=2)
            print(f"✓ 调用链数据已保存: {json_file}\n")
        
        # 如果有AST信息，保存JSON格式
        if ast_info:
            ast_json_file = os.path.join(self.output_dir, f"{safe_path}_ast_{timestamp}.json")
            with open(ast_json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'file_path': file_path,
                    'language': language,
                    'timestamp': datetime.now().isoformat(),
                    'ast_analysis': ast_info
                }, f, ensure_ascii=False, indent=2)
            print(f"✓ AST 数据已保存: {ast_json_file}\n")
    
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
    
    parser = argparse.ArgumentParser(
        description='递归扫描目录下的程序文件并使用 Ollama 进行分析',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  python directory_scanner.py /path/to/project -o reports
  
  # 使用远程 Ollama 服务
  python directory_scanner.py /path/to/project --ollama-url http://192.168.1.100:11434
  
  # 使用不同的模型
  python directory_scanner.py /path/to/project --model qwen2.5:7b
  
  # 只分析特定扩展名的文件
  python directory_scanner.py /path/to/project -e .py .java
  
  # 使用正则表达式过滤文件（只分析包含 "test" 的文件）
  python directory_scanner.py /path/to/project --file-pattern ".*test.*"
  
  # 使用正则表达式过滤目录（只扫描 src 和 lib 目录）
  python directory_scanner.py /path/to/project --dir-pattern "^(src|lib)$"
  
  # 组合使用
  python directory_scanner.py /path/to/project \\
    --ollama-url http://192.168.1.100:11434 \\
    --model qwen2.5:7b \\
    -e .py .java \\
    --file-pattern ".*Service.*" \\
    -o reports
        """
    )
    
    parser.add_argument('directory', help='要扫描的目录路径')
    parser.add_argument('-o', '--output', dest='output_dir', help='分析报告输出目录')
    parser.add_argument('-e', '--extensions', nargs='+', help='要扫描的文件扩展名（例如: .py .java .js）')
    parser.add_argument('--max-size', type=int, default=1024 * 1024, help='最大文件大小（字节），默认 1MB')
    parser.add_argument('--ignore-dirs', nargs='+', help='要忽略的目录名称')
    
    # Ollama 配置参数
    parser.add_argument('--ollama-url', default='http://localhost:11434', 
                       help='Ollama 服务地址（默认: http://localhost:11434）')
    parser.add_argument('--model', default='qwen2.5:0.5b',
                       help='使用的模型名称（默认: qwen2.5:0.5b）')
    
    # 正则表达式过滤参数
    parser.add_argument('--dir-pattern', help='目录名正则表达式（只扫描匹配的目录）')
    parser.add_argument('--file-pattern', help='文件名正则表达式（只分析匹配的文件）')
    
    # 高级分析参数
    parser.add_argument('--enable-call-chain', action='store_true',
                       help='启用函数调用链分析（生成调用图和递归审核）')
    parser.add_argument('--enable-ast', action='store_true',
                       help='启用AST语法分析（提取类、方法、依赖关系）')
    
    args = parser.parse_args()
    
    try:
        scanner = DirectoryScanner(
            root_dir=args.directory,
            output_dir=args.output_dir,
            extensions=args.extensions,
            ignore_dirs=set(args.ignore_dirs) if args.ignore_dirs else None,
            max_file_size=args.max_size,
            ollama_url=args.ollama_url,
            model=args.model,
            dir_pattern=args.dir_pattern,
            file_pattern=args.file_pattern,
            enable_call_chain=args.enable_call_chain,
            enable_ast=args.enable_ast
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

