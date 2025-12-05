# Tests Directory

This directory contains all test files and test reports for the AI Code Analyzer.

## Structure

```
tests/
├── README.md                    # This file
├── TEST_REPORT.md              # General test report
├── PYTHON312_TEST_REPORT.md    # Python 3.12 specific test report
└── graph/                      # Neo4j graph database tests
    ├── test_neo4j.py          # Neo4j integration test script
    └── graph_example.py       # Graph database usage example
```

## Running Tests

### Neo4j Integration Tests

```bash
# Run basic Neo4j tests (no database required)
python3.12 tests/graph/test_neo4j.py

# Run full graph example (requires Neo4j running)
python3.12 tests/graph/graph_example.py examples/
```

### Prerequisites

Install required dependencies:

```bash
pip install -r requirements.txt
```

For Neo4j database tests, start Neo4j:

```bash
cd docker
docker-compose up -d neo4j
```

## Test Reports

### TEST_REPORT.md
Comprehensive test report covering:
- Module imports
- Code parser functionality
- Java/Python parsing
- Directory scanning
- Neo4j client validation

### PYTHON312_TEST_REPORT.md
Python 3.12 specific compatibility report:
- Environment validation
- Dependency verification
- Feature testing
- Performance metrics

## Test Coverage

### ✅ Tested Features

- [x] Module imports
- [x] Code parser creation
- [x] Java code parsing
- [x] Python code parsing
- [x] JavaScript code parsing
- [x] Directory scanning
- [x] Inheritance detection
- [x] Interface detection
- [x] Method extraction
- [x] Parameter parsing
- [x] Return type detection
- [x] Line number tracking
- [x] Neo4j client initialization

### ⏳ Pending Tests

- [ ] Live Neo4j database connection
- [ ] Graph data storage
- [ ] Cypher query execution
- [ ] API endpoint testing
- [ ] Web UI testing

## Writing New Tests

### Test File Template

```python
#!/usr/bin/env python3
"""
Test description
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_feature():
    """Test a specific feature"""
    # Your test code here
    assert True, "Test passed"

if __name__ == "__main__":
    test_feature()
    print("✓ All tests passed")
```

### Test Naming Convention

- `test_*.py` - Test scripts
- `*_example.py` - Usage examples
- `*_REPORT.md` - Test reports

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    pip install -r requirements.txt
    python3 tests/graph/test_neo4j.py
```

## Troubleshooting

### Import Errors

Make sure to run tests from the project root:

```bash
cd /path/to/AICodeAnalyzer
python3 tests/graph/test_neo4j.py
```

### Neo4j Connection Failed

This is expected if Neo4j is not running. Start it with:

```bash
docker-compose -f docker/docker-compose.yml up -d neo4j
```

### Module Not Found

Install dependencies:

```bash
pip install -r requirements.txt
```

## Documentation

- Main README: [../README.md](../README.md)
- Neo4j Guide: [../NEO4J_GUIDE.md](../NEO4J_GUIDE.md)
- Docker Guide: [../docker/README.md](../docker/README.md)
