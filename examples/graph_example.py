#!/usr/bin/env python3
"""
Example script demonstrating Neo4j graph database integration.
This script parses code files and stores them in a knowledge graph.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.neo4j_client import Neo4jClient
from src.graph.code_parser import CodeParser


def main():
    """Main function to demonstrate graph database usage."""
    
    print("=" * 60)
    print("AI Code Analyzer - Neo4j Graph Database Integration")
    print("=" * 60)
    print()
    
    # Configuration
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    
    # Initialize Neo4j client
    print(f"Connecting to Neo4j at {NEO4J_URI}...")
    try:
        neo4j_client = Neo4jClient(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)
        print("✓ Connected successfully")
    except Exception as e:
        print(f"✗ Failed to connect to Neo4j: {e}")
        print("\nPlease ensure Neo4j is running:")
        print("  Docker: docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest")
        print("  Or update connection settings in environment variables")
        return
    
    print()
    
    # Create indexes for better performance
    print("Creating database indexes...")
    neo4j_client.create_indexes()
    print("✓ Indexes created")
    print()
    
    # Optional: Clear existing graph
    clear_graph = input("Clear existing graph data? (y/N): ").strip().lower()
    if clear_graph == 'y':
        print("Clearing graph...")
        neo4j_client.clear_graph()
        print("✓ Graph cleared")
        print()
    
    # Initialize code parser with Neo4j client
    parser = CodeParser(neo4j_client=neo4j_client)
    
    # Get directory to analyze
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = input("Enter directory to analyze (default: examples/): ").strip()
        if not target_dir:
            target_dir = "examples/"
    
    if not os.path.exists(target_dir):
        print(f"✗ Directory not found: {target_dir}")
        neo4j_client.close()
        return
    
    print(f"Analyzing directory: {target_dir}")
    print("-" * 60)
    
    # Parse directory
    results = parser.parse_directory(target_dir)
    
    print()
    print(f"✓ Parsed {len(results)} files")
    print()
    
    # Display statistics
    print("Graph Statistics:")
    print("-" * 60)
    stats = neo4j_client.get_statistics()
    print(f"  Files:       {stats['files']}")
    print(f"  Classes:     {stats['classes']}")
    print(f"  Methods:     {stats['methods']}")
    print(f"  Calls:       {stats['calls']}")
    print(f"  Inheritance: {stats['inheritance']}")
    print()
    
    # Example queries
    print("Example Queries:")
    print("-" * 60)
    
    # Find all classes
    if stats['classes'] > 0:
        print("\n1. Searching for methods containing 'test':")
        methods = neo4j_client.search_methods_by_name("test")
        for method in methods[:5]:  # Show first 5
            print(f"   - {method['class_name']}.{method['name']} ({method['file_path']}:{method['line_start']})")
        
        # Get class hierarchy
        print("\n2. Class hierarchies:")
        # Get first class name from results
        if results and results[0]['classes']:
            first_class = results[0]['classes'][0]['name']
            hierarchy = neo4j_client.get_class_hierarchy(first_class)
            print(f"   Class: {hierarchy['class']}")
            if hierarchy['parents']:
                print(f"   Parents: {', '.join(hierarchy['parents'])}")
            if hierarchy['children']:
                print(f"   Children: {', '.join(hierarchy['children'])}")
    
    print()
    print("-" * 60)
    print("Graph database populated successfully!")
    print()
    print("You can now:")
    print("  1. Open Neo4j Browser at http://localhost:7474")
    print("  2. Run Cypher queries to explore the code graph")
    print("  3. Visualize code structure and dependencies")
    print()
    print("Example Cypher queries:")
    print("  MATCH (f:File)-[:CONTAINS]->(c:Class)-[:HAS_METHOD]->(m:Method) RETURN f,c,m LIMIT 25")
    print("  MATCH (c:Class)-[:EXTENDS]->(p:Class) RETURN c,p")
    print("  MATCH (m1:Method)-[:CALLS]->(m2:Method) RETURN m1,m2")
    print()
    
    # Close connection
    neo4j_client.close()
    print("✓ Connection closed")


if __name__ == "__main__":
    main()
