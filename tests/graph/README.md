# Graph Database Tests

This directory contains tests and examples for Neo4j graph database integration.

## Files

- **test_neo4j.py** - Comprehensive Neo4j integration test suite
- **graph_example.py** - Interactive graph database usage example

## Quick Start

### Run Basic Tests (No Database Required)

```bash
python3.12 tests/graph/test_neo4j.py
```

This will test:
- Module imports
- Code parser functionality
- Java/Python parsing
- Directory scanning
- Neo4j client initialization (without connection)

### Run Full Graph Example (Requires Neo4j)

```bash
# 1. Start Neo4j
docker-compose -f docker/docker-compose.yml up -d neo4j

# 2. Wait for Neo4j to be ready (~30 seconds)
docker-compose -f docker/docker-compose.yml logs -f neo4j

# 3. Run the example
python3.12 tests/graph/graph_example.py examples/

# 4. Access Neo4j Browser
open http://localhost:7474
# Username: neo4j, Password: password
```

## Test Details

### test_neo4j.py

Interactive test script that validates:

1. **Module Imports** - Verify all required modules load
2. **Code Parser** - Test parser creation and initialization
3. **Java Parsing** - Parse Java code with classes, methods, inheritance
4. **Python Parsing** - Parse Python code with type hints
5. **Directory Scanning** - Batch process multiple files
6. **Neo4j Connection** (Optional) - Test database connectivity

**Example Output:**
```
======================================================================
AI Code Analyzer - Neo4j Integration Test
======================================================================

Test 1: Importing modules...
✓ Modules imported successfully

Test 2: Creating code parser...
✓ Code parser created successfully

Test 3: Parsing Java code...
✓ Java parsing test passed
  Class name: TestClass
  Methods: 3

Test 4: Parsing Python code...
✓ Python parsing test passed
  Class name: Calculator
  Methods: 4

Test 5: Parsing example directory...
✓ Parsed 2 files from examples directory

All core tests passed! Neo4j integration is working correctly.
```

### graph_example.py

Interactive example demonstrating:

- Connecting to Neo4j
- Creating indexes
- Parsing code into graph
- Storing nodes and relationships
- Querying the graph
- Viewing statistics

**Example Output:**
```
======================================================================
AI Code Analyzer - Neo4j Graph Database Integration
======================================================================

Connecting to Neo4j at bolt://localhost:7687...
✓ Connected successfully

Creating database indexes...
✓ Indexes created

Analyzing directory: examples/
✓ Parsed 2 files

Graph Statistics:
  Files:       2
  Classes:     4
  Methods:     11
  Calls:       0
  Inheritance: 1

You can now:
  1. Open Neo4j Browser at http://localhost:7474
  2. Run Cypher queries to explore the code graph
  3. Visualize code structure and dependencies
```

## Cypher Query Examples

After running `graph_example.py`, try these queries in Neo4j Browser:

### View All Classes
```cypher
MATCH (c:Class)
RETURN c.name, c.file_path, c.line_start
```

### View Class Methods
```cypher
MATCH (c:Class)-[:HAS_METHOD]->(m:Method)
RETURN c.name as class, m.name as method, m.return_type
```

### View Full Structure
```cypher
MATCH (f:File)-[:CONTAINS]->(c:Class)-[:HAS_METHOD]->(m:Method)
RETURN f, c, m
LIMIT 25
```

### View Inheritance
```cypher
MATCH (c:Class)-[:EXTENDS]->(p:Class)
RETURN c.name as child, p.name as parent
```

### Find Methods by Name
```cypher
MATCH (m:Method)
WHERE m.name CONTAINS 'process'
RETURN m.class_name, m.name, m.parameters
```

## Environment Variables

Configure Neo4j connection:

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
```

## Troubleshooting

### Connection Refused

**Problem:** `ServiceUnavailable: Unable to retrieve routing information`

**Solution:**
```bash
# Check if Neo4j is running
docker-compose -f docker/docker-compose.yml ps neo4j

# Start Neo4j
docker-compose -f docker/docker-compose.yml up -d neo4j

# Wait for startup
docker-compose -f docker/docker-compose.yml logs -f neo4j
```

### Authentication Failed

**Problem:** `AuthError: The client is unauthorized`

**Solution:**
- Default credentials: neo4j/password
- Update in `docker/docker-compose.yml` if changed

### Module Not Found

**Problem:** `ModuleNotFoundError: No module named 'neo4j'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Import Path Issues

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:** Run from project root:
```bash
cd /path/to/AICodeAnalyzer
python3 tests/graph/test_neo4j.py
```

## Performance Tips

### For Large Codebases

1. **Create Indexes First**
   ```python
   client.create_indexes()
   ```

2. **Batch Processing**
   ```python
   # Process files in batches
   for batch in chunks(files, 100):
       parser.parse_files(batch)
   ```

3. **Increase Neo4j Memory**
   Edit `docker/docker-compose.yml`:
   ```yaml
   NEO4J_dbms_memory_heap_max__size=4G
   ```

## Next Steps

1. Run basic tests to verify installation
2. Start Neo4j database
3. Run graph example with sample code
4. Explore data in Neo4j Browser
5. Try custom Cypher queries
6. Integrate with your codebase

## Documentation

- Neo4j Guide: [../../NEO4J_GUIDE.md](../../NEO4J_GUIDE.md)
- Test Reports: [../TEST_REPORT.md](../TEST_REPORT.md)
- Main README: [../../README.md](../../README.md)
