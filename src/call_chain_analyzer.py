#!/usr/bin/env python3
"""
Call Chain Analyzer - 函数调用链分析器
支持提取函数调用关系并递归分析代码
"""

import os
import re
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import json


class CallChainAnalyzer:
    """函数调用链分析器"""
    
    def __init__(self, language: str = 'Java'):
        """
        初始化调用链分析器
        
        Args:
            language: 编程语言（Java, Python, JavaScript等）
        """
        self.language = language
        self.functions = {}  # 函数定义: {function_name: {file, line, code}}
        self.call_graph = defaultdict(set)  # 调用图: {caller: {callees}}
        self.reverse_call_graph = defaultdict(set)  # 反向调用图: {callee: {callers}}
    
    def extract_functions_java(self, content: str, file_path: str) -> List[Dict]:
        """
        提取Java代码中的函数定义
        
        Returns:
            函数列表: [{name, signature, start_line, end_line, code}]
        """
        functions = []
        
        # 匹配方法定义的正则表达式
        # 匹配: public/private/protected [static] [final] ReturnType methodName(params)
        method_pattern = re.compile(
            r'^\s*(public|private|protected)?\s*(static)?\s*(final)?\s*'
            r'(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[\w\s,]+)?\s*\{',
            re.MULTILINE
        )
        
        lines = content.split('\n')
        
        for match in method_pattern.finditer(content):
            method_name = match.group(5)
            params = match.group(6)
            return_type = match.group(4)
            
            # 计算起始行号
            start_pos = match.start()
            start_line = content[:start_pos].count('\n') + 1
            
            # 查找方法结束位置（匹配大括号）
            end_line = self._find_method_end(lines, start_line - 1)
            
            # 提取方法代码
            method_code = '\n'.join(lines[start_line - 1:end_line])
            
            signature = f"{return_type} {method_name}({params})"
            
            functions.append({
                'name': method_name,
                'signature': signature,
                'return_type': return_type,
                'params': params,
                'start_line': start_line,
                'end_line': end_line,
                'code': method_code,
                'file': file_path
            })
        
        return functions
    
    def extract_functions_python(self, content: str, file_path: str) -> List[Dict]:
        """
        提取Python代码中的函数定义
        
        Returns:
            函数列表
        """
        functions = []
        
        # 匹配函数定义
        func_pattern = re.compile(r'^\s*def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([^:]+))?\s*:', re.MULTILINE)
        
        lines = content.split('\n')
        
        for match in func_pattern.finditer(content):
            func_name = match.group(1)
            params = match.group(2)
            return_type = match.group(3) or 'None'
            
            start_pos = match.start()
            start_line = content[:start_pos].count('\n') + 1
            
            # 查找函数结束位置（基于缩进）
            end_line = self._find_python_function_end(lines, start_line - 1)
            
            func_code = '\n'.join(lines[start_line - 1:end_line])
            
            signature = f"def {func_name}({params})"
            
            functions.append({
                'name': func_name,
                'signature': signature,
                'return_type': return_type,
                'params': params,
                'start_line': start_line,
                'end_line': end_line,
                'code': func_code,
                'file': file_path
            })
        
        return functions
    
    def _find_method_end(self, lines: List[str], start_line: int) -> int:
        """查找Java方法的结束行（基于大括号匹配）"""
        brace_count = 0
        in_method = False
        
        for i in range(start_line, len(lines)):
            line = lines[i]
            
            for char in line:
                if char == '{':
                    brace_count += 1
                    in_method = True
                elif char == '}':
                    brace_count -= 1
                    if in_method and brace_count == 0:
                        return i + 1
        
        return len(lines)
    
    def _find_python_function_end(self, lines: List[str], start_line: int) -> int:
        """查找Python函数的结束行（基于缩进）"""
        if start_line >= len(lines):
            return len(lines)
        
        # 获取函数定义的缩进级别
        def_line = lines[start_line]
        base_indent = len(def_line) - len(def_line.lstrip())
        
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            
            # 跳过空行和注释
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # 检查缩进
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent:
                return i
        
        return len(lines)
    
    def extract_function_calls(self, function_code: str, language: str = 'Java') -> Set[str]:
        """
        提取函数中的函数调用
        
        Args:
            function_code: 函数代码
            language: 编程语言
            
        Returns:
            被调用的函数名集合
        """
        calls = set()
        
        if language == 'Java':
            # 匹配方法调用: methodName( 或 object.methodName(
            call_pattern = re.compile(r'(?:^|[^\w])(\w+)\s*\(')
            
            for match in call_pattern.finditer(function_code):
                method_name = match.group(1)
                # 过滤掉关键字和构造函数
                if method_name not in ['if', 'for', 'while', 'switch', 'catch', 'new', 'return']:
                    calls.add(method_name)
        
        elif language == 'Python':
            # 匹配函数调用
            call_pattern = re.compile(r'(?:^|[^\w])(\w+)\s*\(')
            
            for match in call_pattern.finditer(function_code):
                func_name = match.group(1)
                # 过滤掉关键字
                if func_name not in ['if', 'for', 'while', 'with', 'print', 'len', 'range', 'str', 'int', 'list', 'dict']:
                    calls.add(func_name)
        
        return calls
    
    def build_call_graph(self, content: str, file_path: str) -> Dict:
        """
        构建函数调用图
        
        Args:
            content: 文件内容
            file_path: 文件路径
            
        Returns:
            调用图信息
        """
        # 提取函数定义
        if self.language == 'Java':
            functions = self.extract_functions_java(content, file_path)
        elif self.language == 'Python':
            functions = self.extract_functions_python(content, file_path)
        else:
            functions = []
        
        # 存储函数定义
        for func in functions:
            self.functions[func['name']] = func
        
        # 构建调用关系
        for func in functions:
            caller = func['name']
            callees = self.extract_function_calls(func['code'], self.language)
            
            for callee in callees:
                self.call_graph[caller].add(callee)
                self.reverse_call_graph[callee].add(caller)
        
        return {
            'functions': functions,
            'call_graph': {k: list(v) for k, v in self.call_graph.items()},
            'reverse_call_graph': {k: list(v) for k, v in self.reverse_call_graph.items()}
        }
    
    def get_call_chain(self, function_name: str, max_depth: int = 5) -> List[List[str]]:
        """
        获取函数的调用链
        
        Args:
            function_name: 函数名
            max_depth: 最大深度
            
        Returns:
            调用链列表
        """
        chains = []
        
        def dfs(current: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            
            if current in path:  # 检测循环调用
                chains.append(path + [current + " (循环)"])
                return
            
            new_path = path + [current]
            
            if current not in self.call_graph or not self.call_graph[current]:
                chains.append(new_path)
                return
            
            for callee in self.call_graph[current]:
                dfs(callee, new_path, depth + 1)
        
        dfs(function_name, [], 0)
        return chains
    
    def get_reverse_call_chain(self, function_name: str, max_depth: int = 5) -> List[List[str]]:
        """
        获取函数的反向调用链（谁调用了这个函数）
        
        Args:
            function_name: 函数名
            max_depth: 最大深度
            
        Returns:
            反向调用链列表
        """
        chains = []
        
        def dfs(current: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            
            if current in path:
                chains.append([current + " (循环)"] + path)
                return
            
            new_path = [current] + path
            
            if current not in self.reverse_call_graph or not self.reverse_call_graph[current]:
                chains.append(new_path)
                return
            
            for caller in self.reverse_call_graph[current]:
                dfs(caller, new_path, depth + 1)
        
        dfs(function_name, [], 0)
        return chains
    
    def generate_call_chain_report(self) -> str:
        """生成调用链报告"""
        report = []
        
        report.append("# 函数调用链分析报告\n")
        report.append(f"**编程语言**: {self.language}\n")
        report.append(f"**函数总数**: {len(self.functions)}\n")
        report.append(f"**调用关系数**: {sum(len(v) for v in self.call_graph.values())}\n\n")
        
        # 统计信息
        report.append("## 统计信息\n")
        
        # 找出入口函数（没有被调用的函数）
        entry_functions = set(self.functions.keys()) - set(self.reverse_call_graph.keys())
        report.append(f"- **入口函数** (未被其他函数调用): {len(entry_functions)}\n")
        for func in sorted(entry_functions):
            report.append(f"  - `{func}`\n")
        
        # 找出叶子函数（不调用其他函数的函数）
        leaf_functions = set(self.functions.keys()) - set(self.call_graph.keys())
        report.append(f"\n- **叶子函数** (不调用其他函数): {len(leaf_functions)}\n")
        for func in sorted(leaf_functions):
            report.append(f"  - `{func}`\n")
        
        # 详细的调用链
        report.append("\n## 详细调用链\n")
        
        for func_name in sorted(self.functions.keys()):
            func = self.functions[func_name]
            report.append(f"\n### 函数: `{func['signature']}`\n")
            report.append(f"- **文件**: `{func['file']}`\n")
            report.append(f"- **位置**: 第 {func['start_line']}-{func['end_line']} 行\n")
            
            # 正向调用链
            if func_name in self.call_graph and self.call_graph[func_name]:
                report.append(f"- **调用的函数**: {', '.join(f'`{c}`' for c in sorted(self.call_graph[func_name]))}\n")
                
                chains = self.get_call_chain(func_name, max_depth=3)
                if chains:
                    report.append(f"- **调用链** (最多3层):\n")
                    for i, chain in enumerate(chains[:5], 1):  # 只显示前5条
                        report.append(f"  {i}. {' → '.join(chain)}\n")
            
            # 反向调用链
            if func_name in self.reverse_call_graph and self.reverse_call_graph[func_name]:
                report.append(f"- **被调用于**: {', '.join(f'`{c}`' for c in sorted(self.reverse_call_graph[func_name]))}\n")
        
        return ''.join(report)
    
    def generate_mermaid_diagram(self) -> str:
        """生成Mermaid流程图"""
        lines = []
        lines.append("```mermaid")
        lines.append("graph TD")
        
        # 添加节点和边
        for caller, callees in self.call_graph.items():
            for callee in callees:
                lines.append(f"    {caller}[{caller}] --> {callee}[{callee}]")
        
        lines.append("```")
        return '\n'.join(lines)


if __name__ == "__main__":
    # 测试代码
    test_java_code = """
    public class UserService {
        public void createUser(String name) {
            validateUser(name);
            saveUser(name);
            sendNotification(name);
        }
        
        private void validateUser(String name) {
            checkName(name);
        }
        
        private void saveUser(String name) {
            // save to database
        }
        
        private void sendNotification(String name) {
            formatMessage(name);
        }
        
        private void checkName(String name) {
            // validation logic
        }
        
        private String formatMessage(String name) {
            return "Hello " + name;
        }
    }
    """
    
    analyzer = CallChainAnalyzer(language='Java')
    result = analyzer.build_call_graph(test_java_code, "UserService.java")
    
    print("=" * 80)
    print("函数列表:")
    for func in result['functions']:
        print(f"  - {func['signature']}")
    
    print("\n" + "=" * 80)
    print("调用图:")
    for caller, callees in result['call_graph'].items():
        print(f"  {caller} -> {callees}")
    
    print("\n" + "=" * 80)
    print(analyzer.generate_call_chain_report())
    
    print("\n" + "=" * 80)
    print("Mermaid 流程图:")
    print(analyzer.generate_mermaid_diagram())
