# Neo4j Graph Database Integration

## Overview

AI Code Analyzer now includes Neo4j graph database integration for storing and querying code knowledge graphs. This allows you to:

- 📊 Store code structure as a graph (files, classes, methods)
- 🔗 Track relationships (inheritance, method calls, implementations)
- 🔍 Query code dependencies and impact analysis
- 📈 Visualize code architecture
- 🚀 Perform complex graph traversals

## Architecture

### Graph Schema

The knowledge graph consists of the following node types and relationships:

**Nodes:**
- `File`: Source code files
- `Class`: Classes and interfaces
- `Method`: Methods and functions
- `Interface`: Interface definitions

**Relationships:**
- `CONTAINS`: File → Class
- `HAS_METHOD`: Class → Method
- `EXTENDS`: Class → Class (inheritance)
- `IMPLEMENTS`: Class → Interface
- `CALLS`: Method → Method (method calls)

## Quick Start

### 1. Start Neo4j with Docker Compose

```bash
# Start all services including Neo4j
docker-compose up -d

# Check Neo4j status
docker-compose ps neo4j
```

### 2. Access Neo4j Browser

Open your browser and navigate to:
- **URL**: http://localhost:7474
- **Username**: neo4j
- **Password**: password

### 3. Parse Code and Build Graph

```bash
# Run the example script
python3 examples/graph_example.py examples/

# Or specify a custom directory
python3 examples/graph_example.py /path/to/your/code
```

## Usage Examples

### Python API

```python
from src.graph.neo4j_client import Neo4jClient
from src.graph.code_parser import CodeParser

# Connect to Neo4j
client = Neo4jClient(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# Create indexes
client.create_indexes()

# Parse code and store in graph
parser = CodeParser(neo4j_client=client)
results = parser.parse_directory("examples/")

# Query the graph
stats = client.get_statistics()
print(f"Classes: {stats['classes']}")
print(f"Methods: {stats['methods']}")

# Search for methods
methods = client.search_methods_by_name("test")
for method in methods:
    print(f"{method['class_name']}.{method['name']}")

# Get class hierarchy
hierarchy = client.get_class_hierarchy("MyClass")
print(f"Parents: {hierarchy['parents']}")
print(f"Children: {hierarchy['children']}")

# Close connection
client.close()
```

### Manual Node Creation

```python
# Create a file node
client.create_file_node(
    file_path="src/Example.java",
    language="java",
    metadata={"author": "developer"}
)

# Create a class node
client.create_class_node(
    class_name="Example",
    file_path="src/Example.java",
    line_start=10,
    line_end=50,
    metadata={"visibility": "public"}
)

# Create a method node
client.create_method_node(
    method_name="processData",
    class_name="Example",
    file_path="src/Example.java",
    line_start=20,
    line_end=30,
    parameters=["String data", "int count"],
    return_type="boolean"
)

# Create relationships
client.create_inheritance("ChildClass", "ParentClass", "src/Child.java")
client.create_method_call("methodA", "ClassA", "methodB", "ClassB", "src/ClassA.java")
```

## Cypher Query Examples

### Basic Queries

```cypher
// Get all classes
MATCH (c:Class)
RETURN c.name, c.file_path, c.line_start

// Get all methods in a class
MATCH (c:Class {name: 'Example'})-[:HAS_METHOD]->(m:Method)
RETURN m.name, m.return_type, m.parameters

// Find inheritance chains
MATCH path = (c:Class)-[:EXTENDS*]->(parent:Class)
RETURN c.name, parent.name, length(path)

// Find all method calls
MATCH (m1:Method)-[:CALLS]->(m2:Method)
RETURN m1.class_name + '.' + m1.name as caller,
       m2.class_name + '.' + m2.name as callee
```

### Advanced Queries

```cypher
// Find classes with most methods
MATCH (c:Class)-[:HAS_METHOD]->(m:Method)
RETURN c.name, count(m) as method_count
ORDER BY method_count DESC
LIMIT 10

// Find methods that call multiple other methods
MATCH (m:Method)-[:CALLS]->(called:Method)
WITH m, count(called) as call_count
WHERE call_count > 3
RETURN m.class_name + '.' + m.name as method, call_count
ORDER BY call_count DESC

// Find circular dependencies
MATCH path = (c1:Class)-[:EXTENDS*]->(c2:Class)-[:EXTENDS*]->(c1)
RETURN c1.name, c2.name, length(path)

// Get full class structure
MATCH (f:File)-[:CONTAINS]->(c:Class)-[:HAS_METHOD]->(m:Method)
WHERE f.path CONTAINS 'Example'
RETURN f, c, m
```

### Impact Analysis Queries

```cypher
// Find all methods affected by changing a specific method
MATCH (m:Method {name: 'getData'})<-[:CALLS*]-(caller:Method)
RETURN DISTINCT caller.class_name + '.' + caller.name as affected_method

// Find all classes that depend on a class
MATCH (c:Class {name: 'BaseClass'})<-[:EXTENDS*]-(dependent:Class)
RETURN dependent.name, dependent.file_path

// Find orphaned methods (not called by anyone)
MATCH (m:Method)
WHERE NOT (m)<-[:CALLS]-()
RETURN m.class_name + '.' + m.name as orphaned_method
```

## Configuration

### Environment Variables

```bash
# Neo4j connection settings
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
```

### Docker Compose Configuration

Edit `docker-compose.yml` to customize Neo4j settings:

```yaml
neo4j:
  environment:
    - NEO4J_AUTH=neo4j/your_password
    - NEO4J_dbms_memory_heap_max__size=4G  # Increase for large codebases
    - NEO4J_PLUGINS=["apoc", "graph-data-science"]
```

## Performance Tips

1. **Create Indexes**: Always create indexes before bulk imports
   ```python
   client.create_indexes()
   ```

2. **Batch Operations**: For large codebases, use batch processing
   ```python
   # Parse files in batches
   for batch in chunks(files, 100):
       parser.parse_files(batch)
   ```

3. **Memory Configuration**: Adjust Neo4j heap size for large graphs
   ```yaml
   NEO4J_dbms_memory_heap_max__size=4G
   ```

4. **Use APOC**: Enable APOC plugin for advanced operations
   ```cypher
   CALL apoc.periodic.iterate(
     "MATCH (c:Class) RETURN c",
     "SET c.analyzed = true",
     {batchSize:1000}
   )
   ```

## Visualization

### Neo4j Browser

1. Open http://localhost:7474
2. Run visualization queries:
   ```cypher
   // Visualize class hierarchy
   MATCH path = (c:Class)-[:EXTENDS*..3]->(parent:Class)
   RETURN path
   LIMIT 50
   
   // Visualize method calls
   MATCH path = (m1:Method)-[:CALLS]->(m2:Method)
   RETURN path
   LIMIT 100
   ```

### Export Graph Data

```python
# Export to JSON
import json

stats = client.get_statistics()
with open('graph_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

# Export class list
classes = client.search_classes()
with open('classes.csv', 'w') as f:
    f.write('name,file,lines\n')
    for cls in classes:
        f.write(f"{cls['name']},{cls['file_path']},{cls['line_end']-cls['line_start']}\n")
```

## Troubleshooting

### Connection Issues

```bash
# Check if Neo4j is running
docker-compose ps neo4j

# View Neo4j logs
docker-compose logs neo4j

# Restart Neo4j
docker-compose restart neo4j
```

### Clear Graph Data

```python
# Clear all data
client.clear_graph()

# Or use Cypher
# MATCH (n) DETACH DELETE n
```

### Performance Issues

1. Check indexes:
   ```cypher
   SHOW INDEXES
   ```

2. Monitor query performance:
   ```cypher
   PROFILE MATCH (c:Class) RETURN c
   ```

3. Increase memory allocation in docker-compose.yml

## Integration with Existing Features

### With Code Analysis

```python
from src.llm.ollama_client import OllamaClient
from src.graph.neo4j_client import Neo4jClient
from src.graph.code_parser import CodeParser

# Parse code into graph
neo4j_client = Neo4jClient()
parser = CodeParser(neo4j_client=neo4j_client)
parser.parse_file("example.java")

# Get methods from graph
methods = neo4j_client.get_class_methods("Example")

# Analyze each method with LLM
ollama = OllamaClient()
for method in methods:
    # Get method code from file
    analysis = ollama.generate_response(f"Analyze this method: {method['name']}")
    print(analysis)
```

### With Impact Analysis

```python
# Find all methods affected by a change
affected = neo4j_client.get_method_callers("changedMethod", "ChangedClass")

# Analyze impact
for method in affected:
    print(f"Impact on: {method['class_name']}.{method['name']}")
```

## Next Steps

- 📚 Learn Cypher query language: https://neo4j.com/docs/cypher-manual/
- 🔧 Explore APOC procedures: https://neo4j.com/labs/apoc/
- 📊 Try Graph Data Science: https://neo4j.com/docs/graph-data-science/
- 🎨 Build custom visualizations with D3.js or vis.js

## License

MIT License
