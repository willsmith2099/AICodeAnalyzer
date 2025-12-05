"""
Neo4j client for managing code knowledge graph.
"""

from neo4j import GraphDatabase
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jClient:
    """
    Client for interacting with Neo4j graph database.
    Stores code structure as a knowledge graph.
    """
    
    def __init__(self, uri: str = "bolt://localhost:7687", 
                 user: str = "neo4j", 
                 password: str = "password"):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j connection URI
            user: Database username
            password: Database password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info(f"Connected to Neo4j at {uri}")
    
    def close(self):
        """Close the database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def create_indexes(self):
        """Create indexes for better query performance."""
        with self.driver.session() as session:
            # Index for classes
            session.run("CREATE INDEX IF NOT EXISTS FOR (c:Class) ON (c.name)")
            # Index for methods
            session.run("CREATE INDEX IF NOT EXISTS FOR (m:Method) ON (m.name)")
            # Index for files
            session.run("CREATE INDEX IF NOT EXISTS FOR (f:File) ON (f.path)")
            logger.info("Indexes created successfully")
    
    def clear_graph(self):
        """Clear all nodes and relationships from the graph."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Graph cleared")
    
    def create_file_node(self, file_path: str, language: str, metadata: Optional[Dict] = None):
        """
        Create a File node.
        
        Args:
            file_path: Path to the file
            language: Programming language
            metadata: Additional metadata
        """
        with self.driver.session() as session:
            query = """
            MERGE (f:File {path: $path})
            SET f.language = $language,
                f.metadata = $metadata
            RETURN f
            """
            session.run(query, path=file_path, language=language, 
                       metadata=metadata or {})
            logger.info(f"Created File node: {file_path}")
    
    def create_class_node(self, class_name: str, file_path: str, 
                         line_start: int, line_end: int, 
                         metadata: Optional[Dict] = None):
        """
        Create a Class node and link it to a File.
        
        Args:
            class_name: Name of the class
            file_path: Path to the file containing the class
            line_start: Starting line number
            line_end: Ending line number
            metadata: Additional metadata (modifiers, annotations, etc.)
        """
        with self.driver.session() as session:
            query = """
            MATCH (f:File {path: $file_path})
            MERGE (c:Class {name: $class_name, file_path: $file_path})
            SET c.line_start = $line_start,
                c.line_end = $line_end,
                c.metadata = $metadata
            MERGE (f)-[:CONTAINS]->(c)
            RETURN c
            """
            session.run(query, class_name=class_name, file_path=file_path,
                       line_start=line_start, line_end=line_end,
                       metadata=metadata or {})
            logger.info(f"Created Class node: {class_name}")
    
    def create_method_node(self, method_name: str, class_name: str, 
                          file_path: str, line_start: int, line_end: int,
                          parameters: List[str] = None, return_type: str = None,
                          metadata: Optional[Dict] = None):
        """
        Create a Method node and link it to a Class.
        
        Args:
            method_name: Name of the method
            class_name: Name of the containing class
            file_path: Path to the file
            line_start: Starting line number
            line_end: Ending line number
            parameters: List of parameter names
            return_type: Return type of the method
            metadata: Additional metadata (modifiers, annotations, etc.)
        """
        with self.driver.session() as session:
            query = """
            MATCH (c:Class {name: $class_name, file_path: $file_path})
            MERGE (m:Method {name: $method_name, class_name: $class_name, file_path: $file_path})
            SET m.line_start = $line_start,
                m.line_end = $line_end,
                m.parameters = $parameters,
                m.return_type = $return_type,
                m.metadata = $metadata
            MERGE (c)-[:HAS_METHOD]->(m)
            RETURN m
            """
            session.run(query, method_name=method_name, class_name=class_name,
                       file_path=file_path, line_start=line_start, 
                       line_end=line_end, parameters=parameters or [],
                       return_type=return_type, metadata=metadata or {})
            logger.info(f"Created Method node: {class_name}.{method_name}")
    
    def create_method_call(self, caller_method: str, caller_class: str,
                          callee_method: str, callee_class: str,
                          file_path: str):
        """
        Create a CALLS relationship between two methods.
        
        Args:
            caller_method: Name of the calling method
            caller_class: Class containing the caller
            callee_method: Name of the called method
            callee_class: Class containing the callee
            file_path: Path to the file
        """
        with self.driver.session() as session:
            query = """
            MATCH (caller:Method {name: $caller_method, class_name: $caller_class})
            MATCH (callee:Method {name: $callee_method, class_name: $callee_class})
            MERGE (caller)-[:CALLS]->(callee)
            """
            session.run(query, caller_method=caller_method, caller_class=caller_class,
                       callee_method=callee_method, callee_class=callee_class)
            logger.info(f"Created CALLS relationship: {caller_class}.{caller_method} -> {callee_class}.{callee_method}")
    
    def create_inheritance(self, child_class: str, parent_class: str, file_path: str):
        """
        Create an EXTENDS relationship between classes.
        
        Args:
            child_class: Name of the child class
            parent_class: Name of the parent class
            file_path: Path to the file
        """
        with self.driver.session() as session:
            query = """
            MATCH (child:Class {name: $child_class, file_path: $file_path})
            MERGE (parent:Class {name: $parent_class})
            MERGE (child)-[:EXTENDS]->(parent)
            """
            session.run(query, child_class=child_class, parent_class=parent_class,
                       file_path=file_path)
            logger.info(f"Created EXTENDS relationship: {child_class} -> {parent_class}")
    
    def create_implementation(self, class_name: str, interface_name: str, file_path: str):
        """
        Create an IMPLEMENTS relationship between class and interface.
        
        Args:
            class_name: Name of the implementing class
            interface_name: Name of the interface
            file_path: Path to the file
        """
        with self.driver.session() as session:
            query = """
            MATCH (c:Class {name: $class_name, file_path: $file_path})
            MERGE (i:Interface {name: $interface_name})
            MERGE (c)-[:IMPLEMENTS]->(i)
            """
            session.run(query, class_name=class_name, interface_name=interface_name,
                       file_path=file_path)
            logger.info(f"Created IMPLEMENTS relationship: {class_name} -> {interface_name}")
    
    def get_class_methods(self, class_name: str) -> List[Dict]:
        """
        Get all methods of a class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            List of method information
        """
        with self.driver.session() as session:
            query = """
            MATCH (c:Class {name: $class_name})-[:HAS_METHOD]->(m:Method)
            RETURN m.name as name, m.parameters as parameters, 
                   m.return_type as return_type, m.line_start as line_start,
                   m.line_end as line_end
            """
            result = session.run(query, class_name=class_name)
            return [dict(record) for record in result]
    
    def get_method_calls(self, method_name: str, class_name: str) -> List[Dict]:
        """
        Get all methods called by a specific method.
        
        Args:
            method_name: Name of the method
            class_name: Name of the class
            
        Returns:
            List of called methods
        """
        with self.driver.session() as session:
            query = """
            MATCH (m:Method {name: $method_name, class_name: $class_name})-[:CALLS]->(called:Method)
            RETURN called.name as name, called.class_name as class_name
            """
            result = session.run(query, method_name=method_name, class_name=class_name)
            return [dict(record) for record in result]
    
    def get_class_hierarchy(self, class_name: str) -> Dict:
        """
        Get the inheritance hierarchy of a class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            Dictionary with parent and child classes
        """
        with self.driver.session() as session:
            # Get parent classes
            parent_query = """
            MATCH (c:Class {name: $class_name})-[:EXTENDS]->(parent:Class)
            RETURN parent.name as name
            """
            parents = [dict(record)['name'] for record in session.run(parent_query, class_name=class_name)]
            
            # Get child classes
            child_query = """
            MATCH (child:Class)-[:EXTENDS]->(c:Class {name: $class_name})
            RETURN child.name as name
            """
            children = [dict(record)['name'] for record in session.run(child_query, class_name=class_name)]
            
            return {
                'class': class_name,
                'parents': parents,
                'children': children
            }
    
    def search_methods_by_name(self, method_name: str) -> List[Dict]:
        """
        Search for methods by name (supports partial matching).
        
        Args:
            method_name: Method name to search for
            
        Returns:
            List of matching methods
        """
        with self.driver.session() as session:
            query = """
            MATCH (m:Method)
            WHERE m.name CONTAINS $method_name
            RETURN m.name as name, m.class_name as class_name, 
                   m.file_path as file_path, m.line_start as line_start
            """
            result = session.run(query, method_name=method_name)
            return [dict(record) for record in result]
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the code graph.
        
        Returns:
            Dictionary with counts of different node types
        """
        with self.driver.session() as session:
            stats = {}
            
            # Count files
            stats['files'] = session.run("MATCH (f:File) RETURN count(f) as count").single()['count']
            
            # Count classes
            stats['classes'] = session.run("MATCH (c:Class) RETURN count(c) as count").single()['count']
            
            # Count methods
            stats['methods'] = session.run("MATCH (m:Method) RETURN count(m) as count").single()['count']
            
            # Count relationships
            stats['calls'] = session.run("MATCH ()-[r:CALLS]->() RETURN count(r) as count").single()['count']
            stats['inheritance'] = session.run("MATCH ()-[r:EXTENDS]->() RETURN count(r) as count").single()['count']
            
            return stats
