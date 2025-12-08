#!/usr/bin/env python3
"""
AST Static Analyzer - 基于 AST 的静态代码分析器
支持 Java 和 Python 代码的依赖关系分析和影响链追踪
"""

import os
import re
import ast
import subprocess
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import json


class ASTAnalyzer:
    """AST 静态分析器基类"""
    
    def __init__(self, language: str = 'Python'):
        """
        初始化 AST 分析器
        
        Args:
            language: 编程语言（Python, Java）
        """
        self.language = language
        self.classes = {}  # 类定义: {class_name: {file, methods, fields, parent}}
        self.methods = {}  # 方法定义: {method_name: {class, file, calls}}
        self.dependencies = defaultdict(set)  # 依赖关系: {item: {dependencies}}
        self.reverse_dependencies = defaultdict(set)  # 反向依赖: {item: {dependents}}
        self.inheritance = defaultdict(set)  # 继承关系: {child: {parents}}
        self.implementations = defaultdict(set)  # 接口实现: {class: {interfaces}}
    
    def analyze_file(self, file_path: str) -> Dict:
        """
        分析单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            分析结果字典
        """
        if self.language == 'Python':
            return self._analyze_python_file(file_path)
        elif self.language == 'Java':
            return self._analyze_java_file(file_path)
        else:
            raise ValueError(f"Unsupported language: {self.language}")
    
    def _analyze_python_file(self, file_path: str) -> Dict:
        """分析 Python 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
            visitor = PythonASTVisitor(file_path)
            visitor.visit(tree)
            
            return {
                'file': file_path,
                'classes': visitor.classes,
                'functions': visitor.functions,
                'imports': visitor.imports,
                'calls': visitor.calls
            }
        except SyntaxError as e:
            return {
                'file': file_path,
                'error': str(e),
                'classes': [],
                'functions': [],
                'imports': [],
                'calls': []
            }
    
    def _analyze_java_file(self, file_path: str) -> Dict:
        """
        分析 Java 文件（使用正则表达式，简化版）
        
        注意: 完整的 Java AST 分析需要 JavaParser 库
        这里提供基础实现，可以后续扩展
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = {
            'file': file_path,
            'package': self._extract_package(content),
            'imports': self._extract_imports(content),
            'classes': self._extract_java_classes(content, file_path),
            'interfaces': self._extract_interfaces(content),
            'methods': []
        }
        
        return result
    
    def _extract_package(self, content: str) -> Optional[str]:
        """提取 Java 包名"""
        match = re.search(r'package\s+([\w.]+)\s*;', content)
        return match.group(1) if match else None
    
    def _extract_imports(self, content: str) -> List[str]:
        """提取导入语句"""
        imports = []
        for match in re.finditer(r'import\s+([\w.*]+)\s*;', content):
            imports.append(match.group(1))
        return imports
    
    def _extract_java_classes(self, content: str, file_path: str) -> List[Dict]:
        """提取 Java 类定义"""
        classes = []
        
        # 匹配类定义
        class_pattern = re.compile(
            r'(public|private|protected)?\s*(abstract|final)?\s*class\s+(\w+)'
            r'(?:\s+extends\s+([\w.]+))?'
            r'(?:\s+implements\s+([\w\s,]+))?',
            re.MULTILINE
        )
        
        for match in class_pattern.finditer(content):
            class_name = match.group(3)
            parent_class = match.group(4)
            interfaces = match.group(5)
            
            class_info = {
                'name': class_name,
                'file': file_path,
                'parent': parent_class,
                'interfaces': [i.strip() for i in interfaces.split(',')] if interfaces else [],
                'methods': self._extract_class_methods(content, class_name)
            }
            
            classes.append(class_info)
            
            # 记录继承关系
            if parent_class:
                self.inheritance[class_name].add(parent_class)
            
            # 记录接口实现
            if interfaces:
                for interface in class_info['interfaces']:
                    self.implementations[class_name].add(interface.strip())
        
        return classes
    
    def _extract_interfaces(self, content: str) -> List[str]:
        """提取接口定义"""
        interfaces = []
        for match in re.finditer(r'interface\s+(\w+)', content):
            interfaces.append(match.group(1))
        return interfaces
    
    def _extract_class_methods(self, content: str, class_name: str) -> List[Dict]:
        """提取类中的方法"""
        methods = []
        
        # 简化的方法匹配
        method_pattern = re.compile(
            r'(public|private|protected)?\s*(static)?\s*(final)?\s*'
            r'(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)',
            re.MULTILINE
        )
        
        for match in method_pattern.finditer(content):
            method_name = match.group(5)
            return_type = match.group(4)
            params = match.group(6)
            
            methods.append({
                'name': method_name,
                'class': class_name,
                'return_type': return_type,
                'params': params
            })
        
        return methods
    
    def build_dependency_graph(self, files: List[str]) -> Dict:
        """
        构建依赖关系图
        
        Args:
            files: 要分析的文件列表
            
        Returns:
            依赖图信息
        """
        results = []
        
        for file_path in files:
            result = self.analyze_file(file_path)
            results.append(result)
            
            # 构建依赖关系
            if self.language == 'Python':
                self._build_python_dependencies(result)
            elif self.language == 'Java':
                self._build_java_dependencies(result)
        
        return {
            'files': results,
            'dependencies': {k: list(v) for k, v in self.dependencies.items()},
            'reverse_dependencies': {k: list(v) for k, v in self.reverse_dependencies.items()},
            'inheritance': {k: list(v) for k, v in self.inheritance.items()},
            'implementations': {k: list(v) for k, v in self.implementations.items()}
        }
    
    def _build_python_dependencies(self, result: Dict):
        """构建 Python 依赖关系"""
        file_path = result['file']
        
        # 导入依赖
        for imp in result.get('imports', []):
            self.dependencies[file_path].add(imp)
            self.reverse_dependencies[imp].add(file_path)
    
    def _build_java_dependencies(self, result: Dict):
        """构建 Java 依赖关系"""
        file_path = result['file']
        
        # 导入依赖
        for imp in result.get('imports', []):
            self.dependencies[file_path].add(imp)
            self.reverse_dependencies[imp].add(file_path)
        
        # 继承依赖
        for class_info in result.get('classes', []):
            class_name = class_info['name']
            
            if class_info.get('parent'):
                self.dependencies[class_name].add(class_info['parent'])
                self.reverse_dependencies[class_info['parent']].add(class_name)
            
            # 接口依赖
            for interface in class_info.get('interfaces', []):
                self.dependencies[class_name].add(interface)
                self.reverse_dependencies[interface].add(class_name)
    
    def trace_impact(self, changed_items: List[str], max_depth: int = 5) -> Dict:
        """
        追踪变更影响链
        
        Args:
            changed_items: 变更的项目（文件、类、方法）
            max_depth: 最大追踪深度
            
        Returns:
            影响链信息
        """
        upstream_impact = {}  # 向上影响（调用者）
        downstream_impact = {}  # 向下影响（被调用者）
        
        for item in changed_items:
            # 向上追踪（谁依赖这个变更）
            upstream_impact[item] = self._trace_upstream(item, max_depth)
            
            # 向下追踪（这个变更依赖谁）
            downstream_impact[item] = self._trace_downstream(item, max_depth)
        
        return {
            'changed_items': changed_items,
            'upstream_impact': upstream_impact,
            'downstream_impact': downstream_impact,
            'total_affected': self._count_affected(upstream_impact, downstream_impact)
        }
    
    def _trace_upstream(self, item: str, max_depth: int) -> List[List[str]]:
        """向上追踪依赖链（谁依赖我）"""
        chains = []
        visited = set()
        
        def dfs(current: str, path: List[str], depth: int):
            if depth > max_depth or current in visited:
                return
            
            visited.add(current)
            new_path = path + [current]
            
            if current not in self.reverse_dependencies:
                chains.append(new_path)
                return
            
            for dependent in self.reverse_dependencies[current]:
                dfs(dependent, new_path, depth + 1)
        
        dfs(item, [], 0)
        return chains
    
    def _trace_downstream(self, item: str, max_depth: int) -> List[List[str]]:
        """向下追踪依赖链（我依赖谁）"""
        chains = []
        visited = set()
        
        def dfs(current: str, path: List[str], depth: int):
            if depth > max_depth or current in visited:
                return
            
            visited.add(current)
            new_path = path + [current]
            
            if current not in self.dependencies:
                chains.append(new_path)
                return
            
            for dependency in self.dependencies[current]:
                dfs(dependency, new_path, depth + 1)
        
        dfs(item, [], 0)
        return chains
    
    def _count_affected(self, upstream: Dict, downstream: Dict) -> int:
        """统计受影响的项目总数"""
        affected = set()
        
        for chains in upstream.values():
            for chain in chains:
                affected.update(chain)
        
        for chains in downstream.values():
            for chain in chains:
                affected.update(chain)
        
        return len(affected)
    
    def generate_impact_report(self, impact_data: Dict) -> str:
        """生成影响分析报告"""
        report = []
        
        report.append("# 代码变更影响分析报告\n\n")
        report.append(f"**分析语言**: {self.language}\n")
        report.append(f"**变更项目数**: {len(impact_data['changed_items'])}\n")
        report.append(f"**受影响项目总数**: {impact_data['total_affected']}\n\n")
        
        report.append("## 变更项目\n\n")
        for item in impact_data['changed_items']:
            report.append(f"- `{item}`\n")
        
        report.append("\n## 影响链分析\n\n")
        
        for item in impact_data['changed_items']:
            report.append(f"### 变更: `{item}`\n\n")
            
            # 上游影响
            upstream = impact_data['upstream_impact'].get(item, [])
            if upstream:
                report.append("**上游影响** (谁会受影响):\n")
                for i, chain in enumerate(upstream[:5], 1):
                    report.append(f"{i}. {' ← '.join(chain)}\n")
                report.append("\n")
            
            # 下游影响
            downstream = impact_data['downstream_impact'].get(item, [])
            if downstream:
                report.append("**下游影响** (依赖哪些):\n")
                for i, chain in enumerate(downstream[:5], 1):
                    report.append(f"{i}. {' → '.join(chain)}\n")
                report.append("\n")
        
        return ''.join(report)


class PythonASTVisitor(ast.NodeVisitor):
    """Python AST 访问器"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.classes = []
        self.functions = []
        self.imports = []
        self.calls = []
        self.current_class = None
    
    def visit_ClassDef(self, node):
        """访问类定义"""
        class_info = {
            'name': node.name,
            'file': self.file_path,
            'line': node.lineno,
            'bases': [self._get_name(base) for base in node.bases],
            'methods': []
        }
        
        self.current_class = node.name
        self.classes.append(class_info)
        self.generic_visit(node)
        self.current_class = None
    
    def visit_FunctionDef(self, node):
        """访问函数定义"""
        func_info = {
            'name': node.name,
            'file': self.file_path,
            'line': node.lineno,
            'class': self.current_class,
            'args': [arg.arg for arg in node.args.args]
        }
        
        if self.current_class:
            # 添加到类的方法列表
            for cls in self.classes:
                if cls['name'] == self.current_class:
                    cls['methods'].append(func_info)
        else:
            self.functions.append(func_info)
        
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """访问 import 语句"""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """访问 from ... import 语句"""
        module = node.module or ''
        for alias in node.names:
            self.imports.append(f"{module}.{alias.name}" if module else alias.name)
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """访问函数调用"""
        call_name = self._get_name(node.func)
        if call_name:
            self.calls.append(call_name)
        self.generic_visit(node)
    
    def _get_name(self, node):
        """获取节点名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return None


if __name__ == "__main__":
    # 测试代码
    print("AST Static Analyzer - 测试")
    print("=" * 80)
    
    # Python 分析示例
    analyzer = ASTAnalyzer(language='Python')
    
    # 创建测试文件
    test_code = """
class UserService:
    def __init__(self):
        self.db = Database()
    
    def create_user(self, name):
        user = User(name)
        self.validate_user(user)
        self.db.save(user)
        return user
    
    def validate_user(self, user):
        if not user.name:
            raise ValueError("Name required")
"""
    
    with open('/tmp/test_service.py', 'w') as f:
        f.write(test_code)
    
    result = analyzer.analyze_file('/tmp/test_service.py')
    print("\nPython 文件分析结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Java 分析示例
    print("\n" + "=" * 80)
    java_analyzer = ASTAnalyzer(language='Java')
    
    test_java = """
package com.example.service;

import com.example.model.User;
import com.example.repository.UserRepository;

public class UserService extends BaseService implements IUserService {
    private UserRepository userRepository;
    
    public User createUser(String name) {
        User user = new User(name);
        validateUser(user);
        userRepository.save(user);
        return user;
    }
    
    private void validateUser(User user) {
        if (user.getName() == null) {
            throw new IllegalArgumentException("Name required");
        }
    }
}
"""
    
    with open('/tmp/TestService.java', 'w') as f:
        f.write(test_java)
    
    java_result = java_analyzer.analyze_file('/tmp/TestService.java')
    print("\nJava 文件分析结果:")
    print(json.dumps(java_result, indent=2, ensure_ascii=False))
