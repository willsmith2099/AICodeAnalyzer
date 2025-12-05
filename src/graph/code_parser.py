"""
Code parser for extracting structure and building knowledge graph.
"""

import re
import os
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeParser:
    """
    Parser for extracting code structure from source files.
    Supports Java, Python, JavaScript, and more.
    """
    
    def __init__(self, neo4j_client=None):
        """
        Initialize the code parser.
        
        Args:
            neo4j_client: Optional Neo4jClient instance for storing parsed data
        """
        self.neo4j_client = neo4j_client
        self.current_file = None
        self.current_language = None
    
    def parse_file(self, file_path: str, language: str = None) -> Dict:
        """
        Parse a source code file and extract its structure.
        
        Args:
            file_path: Path to the source file
            language: Programming language (auto-detected if not provided)
            
        Returns:
            Dictionary containing parsed structure
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Auto-detect language if not provided
        if language is None:
            language = self._detect_language(file_path)
        
        self.current_file = file_path
        self.current_language = language
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse based on language
        if language.lower() == 'java':
            structure = self._parse_java(content, file_path)
        elif language.lower() == 'python':
            structure = self._parse_python(content, file_path)
        elif language.lower() in ['javascript', 'typescript']:
            structure = self._parse_javascript(content, file_path)
        else:
            logger.warning(f"Unsupported language: {language}")
            structure = {'file': file_path, 'language': language, 'classes': []}
        
        # Store in Neo4j if client is available
        if self.neo4j_client:
            self._store_in_graph(structure)
        
        return structure
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        language_map = {
            '.java': 'java',
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
        }
        return language_map.get(ext, 'unknown')
    
    def _parse_java(self, content: str, file_path: str) -> Dict:
        """
        Parse Java source code.
        
        Args:
            content: Source code content
            file_path: Path to the file
            
        Returns:
            Parsed structure
        """
        structure = {
            'file': file_path,
            'language': 'java',
            'classes': []
        }
        
        lines = content.split('\n')
        
        # Pattern for class declaration
        class_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+|final\s+)?(?:class|interface|enum)\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?'
        
        # Pattern for method declaration
        method_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)'
        
        current_class = None
        brace_count = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Track braces for scope
            brace_count += stripped.count('{') - stripped.count('}')
            
            # Match class declaration
            class_match = re.search(class_pattern, stripped)
            if class_match and brace_count <= 1:
                class_name = class_match.group(1)
                parent_class = class_match.group(2)
                interfaces = class_match.group(3)
                
                current_class = {
                    'name': class_name,
                    'line_start': i,
                    'line_end': None,  # Will be updated when class ends
                    'parent': parent_class,
                    'interfaces': [iface.strip() for iface in interfaces.split(',')] if interfaces else [],
                    'methods': [],
                    'metadata': {}
                }
                structure['classes'].append(current_class)
                logger.debug(f"Found class: {class_name} at line {i}")
            
            # Match method declaration
            method_match = re.search(method_pattern, stripped)
            if method_match and current_class and brace_count > 1:
                return_type = method_match.group(1)
                method_name = method_match.group(2)
                params = method_match.group(3)
                
                # Skip if it's a class constructor (same name as class)
                if method_name != current_class['name']:
                    method_info = {
                        'name': method_name,
                        'return_type': return_type,
                        'parameters': [p.strip() for p in params.split(',') if p.strip()],
                        'line_start': i,
                        'line_end': None,  # Will be updated
                        'metadata': {}
                    }
                    current_class['methods'].append(method_info)
                    logger.debug(f"Found method: {method_name} at line {i}")
            
            # Update class end line when closing brace
            if current_class and brace_count == 0 and '}' in stripped:
                current_class['line_end'] = i
                current_class = None
        
        return structure
    
    def _parse_python(self, content: str, file_path: str) -> Dict:
        """
        Parse Python source code.
        
        Args:
            content: Source code content
            file_path: Path to the file
            
        Returns:
            Parsed structure
        """
        structure = {
            'file': file_path,
            'language': 'python',
            'classes': []
        }
        
        lines = content.split('\n')
        
        # Pattern for class declaration
        class_pattern = r'^class\s+(\w+)(?:\(([^)]+)\))?:'
        
        # Pattern for method declaration
        method_pattern = r'^\s+def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*(.+))?:'
        
        current_class = None
        
        for i, line in enumerate(lines, 1):
            # Match class declaration
            class_match = re.match(class_pattern, line)
            if class_match:
                class_name = class_match.group(1)
                parent_classes = class_match.group(2)
                
                current_class = {
                    'name': class_name,
                    'line_start': i,
                    'line_end': None,
                    'parent': parent_classes.split(',')[0].strip() if parent_classes else None,
                    'interfaces': [],
                    'methods': [],
                    'metadata': {}
                }
                structure['classes'].append(current_class)
                logger.debug(f"Found class: {class_name} at line {i}")
            
            # Match method declaration
            method_match = re.match(method_pattern, line)
            if method_match and current_class:
                method_name = method_match.group(1)
                params = method_match.group(2)
                return_type = method_match.group(3)
                
                method_info = {
                    'name': method_name,
                    'return_type': return_type.strip() if return_type else None,
                    'parameters': [p.strip() for p in params.split(',') if p.strip() and p.strip() != 'self'],
                    'line_start': i,
                    'line_end': None,
                    'metadata': {}
                }
                current_class['methods'].append(method_info)
                logger.debug(f"Found method: {method_name} at line {i}")
            
            # Detect class end (next class or end of indentation)
            if current_class and line and not line.startswith(' ') and not line.startswith('\t') and i > current_class['line_start']:
                if not re.match(class_pattern, line):
                    current_class['line_end'] = i - 1
                    current_class = None
        
        # Handle last class
        if current_class and current_class['line_end'] is None:
            current_class['line_end'] = len(lines)
        
        return structure
    
    def _parse_javascript(self, content: str, file_path: str) -> Dict:
        """
        Parse JavaScript/TypeScript source code.
        
        Args:
            content: Source code content
            file_path: Path to the file
            
        Returns:
            Parsed structure
        """
        structure = {
            'file': file_path,
            'language': 'javascript',
            'classes': []
        }
        
        lines = content.split('\n')
        
        # Pattern for class declaration
        class_pattern = r'(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?'
        
        # Pattern for method declaration
        method_pattern = r'^\s*(?:async\s+)?(\w+)\s*\(([^)]*)\)(?:\s*:\s*(.+))?\s*{'
        
        current_class = None
        brace_count = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Track braces
            brace_count += stripped.count('{') - stripped.count('}')
            
            # Match class declaration
            class_match = re.search(class_pattern, stripped)
            if class_match:
                class_name = class_match.group(1)
                parent_class = class_match.group(2)
                
                current_class = {
                    'name': class_name,
                    'line_start': i,
                    'line_end': None,
                    'parent': parent_class,
                    'interfaces': [],
                    'methods': [],
                    'metadata': {}
                }
                structure['classes'].append(current_class)
                logger.debug(f"Found class: {class_name} at line {i}")
            
            # Match method declaration
            method_match = re.match(method_pattern, stripped)
            if method_match and current_class and brace_count > 1:
                method_name = method_match.group(1)
                params = method_match.group(2)
                return_type = method_match.group(3)
                
                method_info = {
                    'name': method_name,
                    'return_type': return_type.strip() if return_type else None,
                    'parameters': [p.strip() for p in params.split(',') if p.strip()],
                    'line_start': i,
                    'line_end': None,
                    'metadata': {}
                }
                current_class['methods'].append(method_info)
                logger.debug(f"Found method: {method_name} at line {i}")
            
            # Update class end
            if current_class and brace_count == 0 and '}' in stripped:
                current_class['line_end'] = i
                current_class = None
        
        return structure
    
    def _store_in_graph(self, structure: Dict):
        """
        Store parsed structure in Neo4j graph database.
        
        Args:
            structure: Parsed code structure
        """
        if not self.neo4j_client:
            return
        
        file_path = structure['file']
        language = structure['language']
        
        # Create file node
        self.neo4j_client.create_file_node(file_path, language)
        
        # Create class and method nodes
        for class_info in structure['classes']:
            class_name = class_info['name']
            
            # Create class node
            self.neo4j_client.create_class_node(
                class_name=class_name,
                file_path=file_path,
                line_start=class_info['line_start'],
                line_end=class_info['line_end'] or class_info['line_start'],
                metadata=class_info.get('metadata', {})
            )
            
            # Create inheritance relationship
            if class_info.get('parent'):
                self.neo4j_client.create_inheritance(
                    child_class=class_name,
                    parent_class=class_info['parent'],
                    file_path=file_path
                )
            
            # Create interface implementations
            for interface in class_info.get('interfaces', []):
                self.neo4j_client.create_implementation(
                    class_name=class_name,
                    interface_name=interface,
                    file_path=file_path
                )
            
            # Create method nodes
            for method_info in class_info['methods']:
                self.neo4j_client.create_method_node(
                    method_name=method_info['name'],
                    class_name=class_name,
                    file_path=file_path,
                    line_start=method_info['line_start'],
                    line_end=method_info['line_end'] or method_info['line_start'],
                    parameters=method_info.get('parameters', []),
                    return_type=method_info.get('return_type'),
                    metadata=method_info.get('metadata', {})
                )
        
        logger.info(f"Stored structure for {file_path} in graph database")
    
    def parse_directory(self, directory: str, extensions: List[str] = None) -> List[Dict]:
        """
        Parse all source files in a directory.
        
        Args:
            directory: Directory to scan
            extensions: List of file extensions to include (e.g., ['.java', '.py'])
            
        Returns:
            List of parsed structures
        """
        if extensions is None:
            extensions = ['.java', '.py', '.js', '.ts']
        
        results = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    try:
                        structure = self.parse_file(file_path)
                        results.append(structure)
                        logger.info(f"Parsed: {file_path}")
                    except Exception as e:
                        logger.error(f"Error parsing {file_path}: {e}")
        
        return results
