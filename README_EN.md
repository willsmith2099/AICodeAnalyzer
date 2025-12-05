# AI Code Analyzer

[简体中文](README.md) | [English](README_EN.md)

A Python-based tool that leverages locally-running Ollama LLM (qwen2.5:0.5b) to analyze Java code. It can recursively scan specified directories, identify code functionality, potential bugs, and improvement suggestions.

## Project Structure

The project has been refactored into a modular structure for better extensibility:

```text
coderchange/
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image definition (New) 🐳
├── docker-compose.yml     # Docker Compose configuration (New) 🐳
├── .dockerignore          # Docker ignore file (New) 🐳
├── deploy.sh              # Deployment script (New) 🐳
├── DOCKER_DEPLOY.md       # Docker deployment documentation (New) 🐳
├── src/                   # Source code directory
│   ├── analyze_java.py    # Basic code analysis tool
│   ├── analyze_impact.py  # Change impact analysis tool
│   ├── llm/               # LLM client module
│   │   ├── __init__.py
│   │   ├── ollama_client.py    # Ollama API wrapper
│   │   └── git_analyzer.py     # Git change analyzer
│   └── prompts/           # Prompt template module
│       ├── __init__.py
│       ├── java_analysis.py      # Code analysis prompts
│       ├── impact_analysis.py    # Impact analysis prompts
│       └── knowledge_graph.py    # Knowledge graph extraction prompts
├── web/                   # Web interface ⭐
│   ├── app.py             # Flask web application
│   ├── templates/         # HTML templates
│   │   └── index.html
│   └── static/            # Static resources
│       ├── css/style.css
│       └── js/app.js
├── api/                   # REST API ⭐
│   ├── server.py          # API server
│   ├── API_DOCS.md        # API documentation
│   └── test_api.py        # API test script
├── examples/              # Example code
│   └── Test.java          # Test case
├── analysis_results/      # Basic analysis results (auto-generated)
├── impact_reports/        # Impact analysis reports (auto-generated)
├── web_reports/           # Web interface reports (auto-generated)
└── api_reports/           # API reports (auto-generated)
```

## Features

-   **REST API** 🚀⭐: Complete RESTful API interface supporting programmatic calls.
-   **Web Interface** 🌐⭐: Modern web interface supporting online code analysis and report browsing.
-   **Code Analysis**: Automatically analyze Java, Python, JavaScript and other code for functionality, bugs, and improvements.
-   **Change Impact Analysis** ⭐: Analyze the impact scope of code changes based on Git history.
-   **Quality Report Generation** ⭐: Automatically generate professional reports with quality scores and risk assessments.
-   **Modular Design**: LLM calls separated from prompts for easy extension.
-   **Knowledge Graph Support**: Built-in knowledge graph extraction prompt templates (extensible).
-   **Result Output**: Save analysis results to Markdown files in specified directories.
-   **Batch Processing**: Recursively scan all code files in directories.


## Usage Instructions

### Deployment Methods

#### Method 1: Docker Deployment 🐳 (Recommended)

**Quick Start**:
```bash
# Using deployment script (recommended)
./deploy.sh start

# Or using docker-compose
docker-compose up -d
```

**Pull Ollama Model**:
```bash
docker-compose exec ollama ollama pull qwen2.5:0.5b
```

**Access Services**:
- Web Interface: http://localhost:5001
- API Service: http://localhost:8000

Detailed deployment documentation: [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)

#### Method 2: Local Installation

### Prerequisites
1.  Install Python 3.12+
2.  Install and run [Ollama](https://ollama.com/)
3.  Pull model: `ollama pull qwen2.5:0.5b`

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Analysis

#### Mode 1: Web Interface 🌐 (Recommended)

Start the web server:
```bash
python3 web/app.py
```

Then access in browser: `http://localhost:5001`

**Web Interface Features**:
- 📝 Online Code Analysis - Support for Java, Python, JavaScript, etc.
- 📊 Report Browsing - View all historical analysis reports
- 🔍 Repository Scanning - Scan code files in Git repositories
- 🎨 Modern UI - Dark theme, responsive design
- ⚡ Real-time Status - Ollama connection status monitoring

#### Mode 2: Basic Code Analysis

##### 1. Display results in console only
```bash
python3 src/analyze_java.py examples/
```

##### 2. Save results to file (Recommended)
```bash
python3 src/analyze_java.py examples/ analysis_results/
```
This will generate corresponding `*_analysis.md` files for each Java file in the `analysis_results/` directory.

##### 3. Analyze any Java project
```bash
python3 src/analyze_java.py /path/to/your/java/project /path/to/output/directory
```

#### Mode 3: Change Impact Analysis + Quality Report ⭐

**Prerequisites**: Project must be a Git repository

##### 1. Analyze current repository
```bash
python3 src/analyze_impact.py . impact_reports/
```

##### 2. Analyze specified Git repository
```bash
python3 src/analyze_impact.py /path/to/git/repo /path/to/reports
```

**Generated Reports Include**:
- `*_analysis.md` - Code analysis report
- `*_impact.md` - Change impact analysis report
- `quality_reports/*_quality_report.md` - Comprehensive quality report

**Quality Report Contents**:
- Quality Score (1-10)
- Code complexity and maintainability metrics
- Critical issues and warnings
- Change impact assessment
- Testing recommendations
- Action item checklist


## Example Output

After running analysis, the following files will be generated in the specified output directory:
- `Test_analysis.md` - Complete analysis report for `Test.java`

### Analysis Report Example

Each analysis report contains:
1. **Functionality Summary** - Main functionality description of the code
2. **Potential Issues** - Discovered bugs and security vulnerabilities
3. **Improvement Suggestions** - Code optimization and refactoring recommendations

## REST API Usage

### Start API Server

```bash
python3 api/server.py
```

The API server will start at `http://localhost:8000`.

### API Endpoints

- `GET  /api/v1/health` - Health check
- `GET  /api/v1/status` - Status information
- `POST /api/v1/analyze` - Analyze code snippet
- `POST /api/v1/analyze/file` - Analyze file
- `POST /api/v1/analyze/repo` - Analyze repository
- `POST /api/v1/impact` - Impact analysis
- `GET  /api/v1/reports` - Report list
- `GET  /api/v1/reports/<id>` - Get report
- `DEL  /api/v1/reports/<id>` - Delete report

### API Usage Examples

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Analyze code
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "public class Test {...}", "language": "java", "save": true}'

# Get report list
curl http://localhost:8000/api/v1/reports?limit=10
```

For detailed API documentation, see: [API_DOCS.md](api/API_DOCS.md)

### API Testing

```bash
python3 api/test_api.py
```

## Extension Development

### Adding New Prompt Templates

Create a new Python file in the `src/prompts/` directory, for example:

```python
# src/prompts/custom_analysis.py
def get_custom_prompt(content):
    return f"""
    Your custom prompt here...
    {content}
    """
```

### Using Different LLM Models

Modify the `model` parameter in `src/llm/ollama_client.py`:

```python
client = OllamaClient(model="qwen2.5:7b")  # Use a larger model
```

## Technology Stack

- **Python 3.12+**
- **Ollama** - Local LLM runtime environment
- **qwen2.5:0.5b** - Lightweight large language model
- **requests** - HTTP client library
- **GitPython** - Git repository operations library
- **Flask** - Web framework
- **Flask-CORS** - CORS support
- **Markdown** - Markdown rendering library

## Development Roadmap

- [x] Basic code analysis functionality
- [x] Modular architecture refactoring
- [x] File output functionality
- [x] Knowledge graph prompt templates
- [x] Git change analysis integration
- [x] Impact analysis functionality
- [x] Code quality report generation
- [x] Web interface display
- [x] Support for multiple programming languages (Java, Python, JavaScript, etc.)
- [x] REST API interface development
- [x] Docker containerized deployment
- [ ] CI/CD pipeline integration
- [ ] Authentication and authorization system
- [ ] Performance monitoring and logging system

## License

MIT License
