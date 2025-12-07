#!/usr/bin/env python3
"""
Incremental Code Analyzer - 增量代码分析器
只分析新增或修改的代码文件，避免重复分析
"""

import os
import sys
import json
import hashlib
from typing import List, Dict, Set, Optional
from datetime import datetime
from pathlib import Path

# Add the src directory to the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm.ollama_client import OllamaClient
from llm.git_analyzer import GitAnalyzer
from directory_scanner import DirectoryScanner


class AnalysisCache:
    """分析结果缓存管理器"""
    
    def __init__(self, cache_dir: str):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录路径
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "analysis_cache.json"
        self.cache_data = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """加载缓存数据"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  加载缓存失败: {e}，将创建新缓存")
        return {
            'version': '1.0',
            'last_update': None,
            'files': {}
        }
    
    def _save_cache(self):
        """保存缓存数据"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  保存缓存失败: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件内容的 MD5 哈希值"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"⚠️  计算文件哈希失败 {file_path}: {e}")
            return ""
    
    def is_file_changed(self, file_path: str) -> bool:
        """
        检查文件是否已更改
        
        Args:
            file_path: 文件路径
            
        Returns:
            True 如果文件是新的或已修改，False 如果文件未更改
        """
        abs_path = str(Path(file_path).resolve())
        current_hash = self._calculate_file_hash(file_path)
        
        if not current_hash:
            return True  # 无法读取文件，视为已更改
        
        # 检查缓存中是否存在该文件
        if abs_path not in self.cache_data['files']:
            return True  # 新文件
        
        cached_info = self.cache_data['files'][abs_path]
        return cached_info.get('hash') != current_hash
    
    def update_file_cache(self, file_path: str, analysis_result: Dict):
        """
        更新文件缓存信息
        
        Args:
            file_path: 文件路径
            analysis_result: 分析结果
        """
        abs_path = str(Path(file_path).resolve())
        file_hash = self._calculate_file_hash(file_path)
        
        self.cache_data['files'][abs_path] = {
            'hash': file_hash,
            'last_analyzed': datetime.now().isoformat(),
            'status': analysis_result.get('status', 'unknown'),
            'language': analysis_result.get('language', 'unknown')
        }
        self.cache_data['last_update'] = datetime.now().isoformat()
        self._save_cache()
    
    def get_cached_files(self) -> List[str]:
        """获取所有已缓存的文件列表"""
        return list(self.cache_data['files'].keys())
    
    def remove_file_cache(self, file_path: str):
        """删除文件缓存"""
        abs_path = str(Path(file_path).resolve())
        if abs_path in self.cache_data['files']:
            del self.cache_data['files'][abs_path]
            self._save_cache()
    
    def clear_cache(self):
        """清空所有缓存"""
        self.cache_data = {
            'version': '1.0',
            'last_update': None,
            'files': {}
        }
        self._save_cache()
        print("✓ 缓存已清空")
    
    def get_statistics(self) -> Dict:
        """获取缓存统计信息"""
        return {
            'total_cached_files': len(self.cache_data['files']),
            'last_update': self.cache_data.get('last_update'),
            'cache_file': str(self.cache_file)
        }


class IncrementalAnalyzer:
    """增量代码分析器"""
    
    def __init__(self, root_dir: str, output_dir: str = None, cache_dir: str = None,
                 extensions: List[str] = None, use_git: bool = True):
        """
        初始化增量分析器
        
        Args:
            root_dir: 项目根目录
            output_dir: 分析报告输出目录
            cache_dir: 缓存目录（默认为 output_dir/.cache）
            extensions: 要分析的文件扩展名列表
            use_git: 是否使用 Git 来检测变更
        """
        self.root_dir = Path(root_dir).resolve()
        self.output_dir = Path(output_dir) if output_dir else self.root_dir / "incremental_reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化缓存
        cache_path = cache_dir if cache_dir else self.output_dir / ".cache"
        self.cache = AnalysisCache(str(cache_path))
        
        # 初始化扫描器
        self.scanner = DirectoryScanner(
            root_dir=str(self.root_dir),
            output_dir=str(self.output_dir),
            extensions=extensions
        )
        
        # 初始化 Git 分析器（如果可用）
        self.use_git = use_git
        self.git_analyzer = None
        if use_git:
            try:
                self.git_analyzer = GitAnalyzer(str(self.root_dir))
                print("✓ Git 仓库检测成功，将使用 Git 来检测文件变更\n")
            except ValueError:
                print("⚠️  不是 Git 仓库，将使用文件哈希来检测变更\n")
                self.use_git = False
        
        self.ollama_client = OllamaClient()
        self.stats = {
            'total_files': 0,
            'new_files': 0,
            'modified_files': 0,
            'unchanged_files': 0,
            'analyzed_files': 0,
            'failed_files': 0
        }
    
    def get_changed_files_from_git(self, since_commit: str = None) -> Set[str]:
        """
        从 Git 获取已更改的文件列表
        
        Args:
            since_commit: 起始提交哈希（默认为上次提交）
            
        Returns:
            已更改文件的路径集合
        """
        if not self.git_analyzer:
            return set()
        
        try:
            changed_files = self.git_analyzer.get_changed_files(since_commit)
            # 转换为绝对路径
            return {str((self.root_dir / f).resolve()) for f in changed_files if f}
        except Exception as e:
            print(f"⚠️  获取 Git 变更失败: {e}")
            return set()
    
    def scan_and_filter_files(self, force_all: bool = False) -> Dict[str, List[str]]:
        """
        扫描目录并过滤出需要分析的文件
        
        Args:
            force_all: 是否强制分析所有文件
            
        Returns:
            分类后的文件字典：{'new': [...], 'modified': [...], 'unchanged': [...]}
        """
        print("🔍 开始扫描项目文件...\n")
        
        all_files = self.scanner.scan_directory()
        self.stats['total_files'] = len(all_files)
        
        categorized = {
            'new': [],
            'modified': [],
            'unchanged': []
        }
        
        if force_all:
            print("⚡ 强制分析模式：将分析所有文件\n")
            categorized['modified'] = all_files
            self.stats['modified_files'] = len(all_files)
            return categorized
        
        # 获取 Git 变更的文件（如果可用）
        git_changed_files = self.get_changed_files_from_git() if self.use_git else set()
        
        print("📊 正在分类文件...\n")
        for file_path in all_files:
            abs_path = str(Path(file_path).resolve())
            
            # 检查文件是否在缓存中
            is_cached = abs_path in self.cache.get_cached_files()
            
            # 检查文件是否已更改
            if self.use_git and git_changed_files:
                # 使用 Git 检测
                is_changed = abs_path in git_changed_files
            else:
                # 使用文件哈希检测
                is_changed = self.cache.is_file_changed(file_path)
            
            if not is_cached:
                categorized['new'].append(file_path)
                self.stats['new_files'] += 1
            elif is_changed:
                categorized['modified'].append(file_path)
                self.stats['modified_files'] += 1
            else:
                categorized['unchanged'].append(file_path)
                self.stats['unchanged_files'] += 1
        
        return categorized
    
    def analyze_incremental(self, force_all: bool = False, verbose: bool = True) -> List[Dict]:
        """
        执行增量分析
        
        Args:
            force_all: 是否强制分析所有文件
            verbose: 是否显示详细信息
            
        Returns:
            分析结果列表
        """
        print("="*80)
        print("🚀 增量代码分析器")
        print("="*80)
        print(f"项目目录: {self.root_dir}")
        print(f"输出目录: {self.output_dir}")
        print(f"缓存目录: {self.cache.cache_dir}")
        print("="*80 + "\n")
        
        # 显示缓存统计
        cache_stats = self.cache.get_statistics()
        print(f"📦 缓存信息:")
        print(f"  - 已缓存文件: {cache_stats['total_cached_files']}")
        print(f"  - 上次更新: {cache_stats['last_update'] or '从未'}")
        print()
        
        # 扫描并分类文件
        categorized_files = self.scan_and_filter_files(force_all)
        
        # 显示分类统计
        print("📈 文件分类统计:")
        print(f"  - 总文件数: {self.stats['total_files']}")
        print(f"  - 新文件: {self.stats['new_files']}")
        print(f"  - 已修改: {self.stats['modified_files']}")
        print(f"  - 未更改: {self.stats['unchanged_files']}")
        print()
        
        # 需要分析的文件
        files_to_analyze = categorized_files['new'] + categorized_files['modified']
        
        if not files_to_analyze:
            print("✅ 没有需要分析的文件！所有文件都是最新的。\n")
            return []
        
        print(f"🎯 将分析 {len(files_to_analyze)} 个文件\n")
        
        # 分析文件
        results = []
        for i, file_path in enumerate(files_to_analyze, 1):
            print(f"\n进度: [{i}/{len(files_to_analyze)}]")
            
            # 使用 DirectoryScanner 的分析方法
            result = self.scanner.analyze_file(file_path)
            results.append(result)
            
            # 更新缓存
            if result['status'] == 'success':
                self.cache.update_file_cache(file_path, result)
                self.stats['analyzed_files'] += 1
            else:
                self.stats['failed_files'] += 1
        
        # 打印最终统计
        self._print_summary()
        
        # 保存增量分析报告
        self._save_incremental_report(categorized_files, results)
        
        return results
    
    def _print_summary(self):
        """打印分析统计摘要"""
        print("\n" + "="*80)
        print("📊 增量分析统计")
        print("="*80)
        print(f"扫描的文件总数: {self.stats['total_files']}")
        print(f"新文件: {self.stats['new_files']}")
        print(f"已修改文件: {self.stats['modified_files']}")
        print(f"未更改文件: {self.stats['unchanged_files']}")
        print(f"成功分析: {self.stats['analyzed_files']}")
        print(f"分析失败: {self.stats['failed_files']}")
        print("="*80)
    
    def _save_incremental_report(self, categorized_files: Dict, results: List[Dict]):
        """保存增量分析报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.output_dir / f"incremental_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 增量代码分析报告\n\n")
            f.write(f"**项目目录**: `{self.root_dir}`\n\n")
            f.write(f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**分析模式**: {'Git 变更检测' if self.use_git else '文件哈希检测'}\n\n")
            
            f.write("## 📊 统计信息\n\n")
            f.write(f"- 扫描的文件总数: {self.stats['total_files']}\n")
            f.write(f"- 新文件: {self.stats['new_files']}\n")
            f.write(f"- 已修改文件: {self.stats['modified_files']}\n")
            f.write(f"- 未更改文件: {self.stats['unchanged_files']}\n")
            f.write(f"- 成功分析: {self.stats['analyzed_files']}\n")
            f.write(f"- 分析失败: {self.stats['failed_files']}\n\n")
            
            # 新文件列表
            if categorized_files['new']:
                f.write("## 🆕 新文件\n\n")
                for file_path in categorized_files['new']:
                    rel_path = os.path.relpath(file_path, self.root_dir)
                    f.write(f"- `{rel_path}`\n")
                f.write("\n")
            
            # 已修改文件列表
            if categorized_files['modified']:
                f.write("## ✏️ 已修改文件\n\n")
                for file_path in categorized_files['modified']:
                    rel_path = os.path.relpath(file_path, self.root_dir)
                    f.write(f"- `{rel_path}`\n")
                f.write("\n")
            
            # 分析结果摘要
            f.write("## 📝 分析结果\n\n")
            for result in results:
                status_emoji = "✅" if result['status'] == 'success' else "❌"
                f.write(f"{status_emoji} **{result['file_path']}** ({result['language']})\n")
                if result['error']:
                    f.write(f"   - 错误: {result['error']}\n")
                f.write("\n")
        
        print(f"\n✓ 增量分析报告已保存: {report_file}")
    
    def clear_cache(self):
        """清空分析缓存"""
        self.cache.clear_cache()
    
    def show_cache_info(self):
        """显示缓存信息"""
        stats = self.cache.get_statistics()
        print("\n" + "="*80)
        print("📦 缓存信息")
        print("="*80)
        print(f"缓存文件: {stats['cache_file']}")
        print(f"已缓存文件数: {stats['total_cached_files']}")
        print(f"上次更新: {stats['last_update'] or '从未'}")
        print("="*80 + "\n")
        
        if stats['total_cached_files'] > 0:
            print("已缓存的文件列表:")
            for i, file_path in enumerate(self.cache.get_cached_files()[:10], 1):
                print(f"  {i}. {file_path}")
            if stats['total_cached_files'] > 10:
                print(f"  ... 还有 {stats['total_cached_files'] - 10} 个文件")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='增量代码分析器 - 只分析新增或修改的代码文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 增量分析当前目录
  python3 src/incremental_analyzer.py . -o reports
  
  # 强制分析所有文件
  python3 src/incremental_analyzer.py . -o reports --force
  
  # 只分析 Python 和 Java 文件
  python3 src/incremental_analyzer.py . -o reports -e .py .java
  
  # 显示缓存信息
  python3 src/incremental_analyzer.py . --show-cache
  
  # 清空缓存
  python3 src/incremental_analyzer.py . --clear-cache
        """
    )
    
    parser.add_argument('directory', help='要分析的项目目录')
    parser.add_argument('-o', '--output', dest='output_dir', help='分析报告输出目录')
    parser.add_argument('-c', '--cache-dir', dest='cache_dir', help='缓存目录（默认为输出目录/.cache）')
    parser.add_argument('-e', '--extensions', nargs='+', help='要分析的文件扩展名（例如: .py .java .js）')
    parser.add_argument('--force', action='store_true', help='强制分析所有文件，忽略缓存')
    parser.add_argument('--no-git', action='store_true', help='不使用 Git 检测变更，只使用文件哈希')
    parser.add_argument('--show-cache', action='store_true', help='显示缓存信息')
    parser.add_argument('--clear-cache', action='store_true', help='清空缓存')
    
    args = parser.parse_args()
    
    try:
        analyzer = IncrementalAnalyzer(
            root_dir=args.directory,
            output_dir=args.output_dir,
            cache_dir=args.cache_dir,
            extensions=args.extensions,
            use_git=not args.no_git
        )
        
        if args.show_cache:
            analyzer.show_cache_info()
            return
        
        if args.clear_cache:
            analyzer.clear_cache()
            return
        
        analyzer.analyze_incremental(force_all=args.force)
        
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
