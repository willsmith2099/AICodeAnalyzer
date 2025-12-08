#!/usr/bin/env python3
"""
Git Change Analyzer - Git 变更分析器
结合 Git Diff 和 AST 分析追踪代码变更影响
"""

import os
import subprocess
import re
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime
import json

from ast_analyzer import ASTAnalyzer


class GitChangeAnalyzer:
    """Git 变更分析器"""
    
    def __init__(self, repo_path: str, language: str = 'Java'):
        """
        初始化 Git 变更分析器
        
        Args:
            repo_path: Git 仓库路径
            language: 编程语言
        """
        self.repo_path = os.path.abspath(repo_path)
        self.language = language
        self.ast_analyzer = ASTAnalyzer(language=language)
        
        if not os.path.isdir(os.path.join(self.repo_path, '.git')):
            raise ValueError(f"Not a git repository: {self.repo_path}")
    
    def get_changed_files(self, commit_range: str = 'HEAD~1..HEAD') -> List[str]:
        """
        获取变更的文件列表
        
        Args:
            commit_range: Git commit 范围，如 'HEAD~1..HEAD' 或 'main..feature'
            
        Returns:
            变更文件列表
        """
        cmd = ['git', 'diff', '--name-only', commit_range]
        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Git command failed: {result.stderr}")
        
        files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        
        # 过滤指定语言的文件
        if self.language == 'Java':
            files = [f for f in files if f.endswith('.java')]
        elif self.language == 'Python':
            files = [f for f in files if f.endswith('.py')]
        
        return files
    
    def get_file_diff(self, file_path: str, commit_range: str = 'HEAD~1..HEAD') -> Dict:
        """
        获取文件的详细变更
        
        Args:
            file_path: 文件路径
            commit_range: Git commit 范围
            
        Returns:
            变更详情
        """
        cmd = ['git', 'diff', commit_range, '--', file_path]
        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {'file': file_path, 'error': result.stderr}
        
        diff_content = result.stdout
        
        return {
            'file': file_path,
            'diff': diff_content,
            'changed_lines': self._parse_changed_lines(diff_content),
            'added_lines': self._count_lines(diff_content, '+'),
            'deleted_lines': self._count_lines(diff_content, '-')
        }
    
    def _parse_changed_lines(self, diff_content: str) -> List[Tuple[int, str]]:
        """解析变更的行号和内容"""
        changed_lines = []
        current_line = 0
        
        for line in diff_content.split('\n'):
            # 解析行号信息
            if line.startswith('@@'):
                match = re.search(r'\+(\d+)', line)
                if match:
                    current_line = int(match.group(1))
            elif line.startswith('+') and not line.startswith('+++'):
                changed_lines.append((current_line, line[1:]))
                current_line += 1
            elif not line.startswith('-'):
                current_line += 1
        
        return changed_lines
    
    def _count_lines(self, diff_content: str, prefix: str) -> int:
        """统计添加或删除的行数"""
        count = 0
        for line in diff_content.split('\n'):
            if line.startswith(prefix) and not line.startswith(f'{prefix}{prefix}{prefix}'):
                count += 1
        return count
    
    def extract_changed_items(self, file_path: str, changed_lines: List[Tuple[int, str]]) -> List[str]:
        """
        从变更的行中提取变更的项目（类、方法、变量）
        
        Args:
            file_path: 文件路径
            changed_lines: 变更的行号和内容
            
        Returns:
            变更项目列表
        """
        changed_items = set()
        
        # 分析文件获取结构信息
        full_path = os.path.join(self.repo_path, file_path)
        if not os.path.exists(full_path):
            return list(changed_items)
        
        file_analysis = self.ast_analyzer.analyze_file(full_path)
        
        # 根据行号匹配变更的类和方法
        for line_no, content in changed_lines:
            # 匹配类
            if self.language == 'Java':
                for class_info in file_analysis.get('classes', []):
                    changed_items.add(f"{file_path}::{class_info['name']}")
                    
                    # 匹配方法
                    for method in class_info.get('methods', []):
                        changed_items.add(f"{file_path}::{class_info['name']}.{method['name']}")
            
            elif self.language == 'Python':
                for class_info in file_analysis.get('classes', []):
                    if abs(class_info['line'] - line_no) < 50:  # 简化判断
                        changed_items.add(f"{file_path}::{class_info['name']}")
                        
                        for method in class_info.get('methods', []):
                            if abs(method['line'] - line_no) < 20:
                                changed_items.add(f"{file_path}::{class_info['name']}.{method['name']}")
        
        return list(changed_items)
    
    def analyze_change_impact(self, commit_range: str = 'HEAD~1..HEAD', max_depth: int = 5) -> Dict:
        """
        分析代码变更的影响
        
        Args:
            commit_range: Git commit 范围
            max_depth: 影响链追踪深度
            
        Returns:
            影响分析结果
        """
        # 1. 获取变更文件
        changed_files = self.get_changed_files(commit_range)
        
        if not changed_files:
            return {
                'commit_range': commit_range,
                'changed_files': [],
                'changed_items': [],
                'impact': {},
                'summary': '没有检测到代码变更'
            }
        
        # 2. 提取变更点
        all_changed_items = []
        file_details = []
        
        for file_path in changed_files:
            diff_info = self.get_file_diff(file_path, commit_range)
            changed_items = self.extract_changed_items(
                file_path,
                diff_info.get('changed_lines', [])
            )
            
            all_changed_items.extend(changed_items)
            file_details.append({
                'file': file_path,
                'added_lines': diff_info.get('added_lines', 0),
                'deleted_lines': diff_info.get('deleted_lines', 0),
                'changed_items': changed_items
            })
        
        # 3. 构建依赖图
        all_files = self._get_all_project_files()
        dependency_graph = self.ast_analyzer.build_dependency_graph(all_files)
        
        # 4. 追踪影响链
        impact_data = self.ast_analyzer.trace_impact(all_changed_items, max_depth)
        
        # 5. 生成报告
        return {
            'commit_range': commit_range,
            'analysis_time': datetime.now().isoformat(),
            'changed_files': changed_files,
            'file_details': file_details,
            'changed_items': all_changed_items,
            'impact': impact_data,
            'dependency_graph': dependency_graph,
            'summary': self._generate_summary(file_details, impact_data)
        }
    
    def _get_all_project_files(self) -> List[str]:
        """获取项目中所有相关文件"""
        files = []
        
        for root, dirs, filenames in os.walk(self.repo_path):
            # 跳过 .git 目录
            if '.git' in root:
                continue
            
            for filename in filenames:
                if self.language == 'Java' and filename.endswith('.java'):
                    files.append(os.path.join(root, filename))
                elif self.language == 'Python' and filename.endswith('.py'):
                    files.append(os.path.join(root, filename))
        
        return files
    
    def _generate_summary(self, file_details: List[Dict], impact_data: Dict) -> str:
        """生成摘要"""
        total_files = len(file_details)
        total_added = sum(f.get('added_lines', 0) for f in file_details)
        total_deleted = sum(f.get('deleted_lines', 0) for f in file_details)
        total_affected = impact_data.get('total_affected', 0)
        
        return (
            f"变更了 {total_files} 个文件，"
            f"新增 {total_added} 行，删除 {total_deleted} 行，"
            f"影响 {total_affected} 个项目"
        )
    
    def generate_report(self, analysis_result: Dict, output_file: Optional[str] = None) -> str:
        """
        生成影响分析报告
        
        Args:
            analysis_result: 分析结果
            output_file: 输出文件路径（可选）
            
        Returns:
            报告内容
        """
        report = []
        
        report.append("# Git 代码变更影响分析报告\n\n")
        report.append(f"**Commit 范围**: `{analysis_result['commit_range']}`\n")
        report.append(f"**分析时间**: {analysis_result['analysis_time']}\n")
        report.append(f"**编程语言**: {self.language}\n\n")
        
        report.append("## 摘要\n\n")
        report.append(f"{analysis_result['summary']}\n\n")
        
        report.append("## 变更文件\n\n")
        for detail in analysis_result['file_details']:
            report.append(f"### `{detail['file']}`\n")
            report.append(f"- 新增行数: {detail['added_lines']}\n")
            report.append(f"- 删除行数: {detail['deleted_lines']}\n")
            report.append(f"- 变更项目: {len(detail['changed_items'])}\n")
            
            if detail['changed_items']:
                report.append("\n变更的类/方法:\n")
                for item in detail['changed_items']:
                    report.append(f"- `{item}`\n")
            report.append("\n")
        
        report.append("## 影响分析\n\n")
        impact = analysis_result['impact']
        
        for item in impact.get('changed_items', [])[:10]:  # 只显示前10个
            report.append(f"### 变更: `{item}`\n\n")
            
            upstream = impact['upstream_impact'].get(item, [])
            if upstream:
                report.append("**上游影响** (谁会受影响):\n")
                for i, chain in enumerate(upstream[:3], 1):
                    report.append(f"{i}. {' ← '.join(chain[:5])}\n")
                report.append("\n")
            
            downstream = impact['downstream_impact'].get(item, [])
            if downstream:
                report.append("**下游影响** (依赖哪些):\n")
                for i, chain in enumerate(downstream[:3], 1):
                    report.append(f"{i}. {' → '.join(chain[:5])}\n")
                report.append("\n")
        
        report.append("## 建议\n\n")
        report.append("基于影响分析，建议:\n")
        report.append(f"1. 重点测试受影响的 {impact.get('total_affected', 0)} 个项目\n")
        report.append("2. 检查上游调用者的兼容性\n")
        report.append("3. 验证下游依赖的可用性\n")
        report.append("4. 更新相关文档和测试用例\n")
        
        report_content = ''.join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"✓ 报告已保存: {output_file}")
        
        return report_content


if __name__ == "__main__":
    import sys
    
    # 测试代码
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
        commit_range = sys.argv[2] if len(sys.argv) > 2 else 'HEAD~1..HEAD'
    else:
        repo_path = '.'
        commit_range = 'HEAD~1..HEAD'
    
    print("Git Change Analyzer - 测试")
    print("=" * 80)
    print(f"仓库路径: {repo_path}")
    print(f"Commit 范围: {commit_range}")
    print()
    
    try:
        analyzer = GitChangeAnalyzer(repo_path, language='Python')
        
        # 分析变更影响
        result = analyzer.analyze_change_impact(commit_range)
        
        # 生成报告
        report = analyzer.generate_report(result, 'change_impact_report.md')
        print(report)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
