from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.ollama_client import OllamaClient
from src.llm.git_analyzer import GitAnalyzer
from src.prompts.java_analysis import get_java_analysis_prompt
from src.prompts.impact_analysis import get_impact_analysis_prompt, get_quality_report_prompt

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# API Configuration
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Reports directory
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'api_reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.route(f'{API_PREFIX}/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        200: Service is healthy
        503: Service is unhealthy
    """
    try:
        client = OllamaClient()
        return jsonify({
            'status': 'healthy',
            'version': API_VERSION,
            'timestamp': datetime.now().isoformat(),
            'ollama': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'version': API_VERSION,
            'timestamp': datetime.now().isoformat(),
            'ollama': 'disconnected',
            'error': str(e)
        }), 503

@app.route(f'{API_PREFIX}/status', methods=['GET'])
def get_status():
    """Get API status and statistics"""
    try:
        # Count reports
        total_reports = sum(1 for _ in os.walk(REPORTS_DIR) for f in _[2] if f.endswith('.md'))
        
        return jsonify({
            'version': API_VERSION,
            'timestamp': datetime.now().isoformat(),
            'reports_directory': REPORTS_DIR,
            'total_reports': total_reports,
            'supported_languages': ['java', 'python', 'javascript', 'typescript'],
            'endpoints': {
                'health': f'{API_PREFIX}/health',
                'analyze': f'{API_PREFIX}/analyze',
                'analyze_file': f'{API_PREFIX}/analyze/file',
                'analyze_repo': f'{API_PREFIX}/analyze/repo',
                'reports': f'{API_PREFIX}/reports',
                'impact': f'{API_PREFIX}/impact'
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Code Analysis Endpoints
# ============================================================================

@app.route(f'{API_PREFIX}/analyze', methods=['POST'])
def analyze_code():
    """
    Analyze code snippet
    
    Request Body:
        {
            "code": "string (required)",
            "language": "string (optional, default: java)",
            "save": "boolean (optional, default: false)"
        }
    
    Returns:
        200: Analysis result
        400: Bad request
        500: Internal error
    """
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({'error': 'Code is required'}), 400
        
        code = data['code']
        language = data.get('language', 'java')
        save_report = data.get('save', False)
        
        # Initialize client
        client = OllamaClient()
        
        # Generate prompt based on language
        if language == 'java':
            prompt = get_java_analysis_prompt('snippet', code)
        else:
            prompt = f"""
            You are an expert {language} code reviewer. Analyze the following code:
            
            ```{language}
            {code}
            ```
            
            Provide:
            1. Functionality summary
            2. Potential bugs or issues
            3. Improvement suggestions
            
            Output in Markdown format.
            """
        
        # Get analysis
        analysis = client.generate_response(prompt)
        
        # Save if requested
        report_id = None
        if save_report:
            report_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            report_path = os.path.join(REPORTS_DIR, report_id)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"# Code Analysis\n\n")
                f.write(f"**Language**: {language}\n\n")
                f.write(f"**Timestamp**: {datetime.now().isoformat()}\n\n")
                f.write(f"## Code\n\n```{language}\n{code}\n```\n\n")
                f.write(f"## Analysis\n\n{analysis}\n")
        
        return jsonify({
            'success': True,
            'language': language,
            'analysis': analysis,
            'report_id': report_id,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route(f'{API_PREFIX}/analyze/file', methods=['POST'])
def analyze_file():
    """
    Analyze a code file
    
    Request Body:
        {
            "file_path": "string (required)",
            "language": "string (optional, auto-detect from extension)"
        }
    
    Returns:
        200: Analysis result
        400: Bad request
        404: File not found
        500: Internal error
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify({'error': 'file_path is required'}), 400
        
        file_path = data['file_path']
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Auto-detect language
        ext = os.path.splitext(file_path)[1]
        language_map = {
            '.java': 'java',
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript'
        }
        language = data.get('language', language_map.get(ext, 'unknown'))
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Analyze
        client = OllamaClient()
        
        if language == 'java':
            prompt = get_java_analysis_prompt(file_path, code)
        else:
            prompt = f"""
            Analyze this {language} file: {file_path}
            
            ```{language}
            {code}
            ```
            
            Provide detailed analysis including functionality, issues, and suggestions.
            """
        
        analysis = client.generate_response(prompt)
        
        # Save report
        report_id = f"{os.path.basename(file_path)}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join(REPORTS_DIR, report_id)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Analysis: {file_path}\n\n")
            f.write(analysis)
        
        return jsonify({
            'success': True,
            'file_path': file_path,
            'language': language,
            'analysis': analysis,
            'report_id': report_id,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route(f'{API_PREFIX}/analyze/repo', methods=['POST'])
def analyze_repository():
    """
    Analyze a Git repository
    
    Request Body:
        {
            "repo_path": "string (required)",
            "max_files": "integer (optional, default: 20)"
        }
    
    Returns:
        200: Repository analysis started
        400: Bad request
        500: Internal error
    """
    try:
        data = request.get_json()
        
        if not data or 'repo_path' not in data:
            return jsonify({'error': 'repo_path is required'}), 400
        
        repo_path = data['repo_path']
        max_files = data.get('max_files', 20)
        
        if not os.path.exists(repo_path):
            return jsonify({'error': 'Repository path not found'}), 404
        
        # Initialize Git Analyzer
        try:
            git_analyzer = GitAnalyzer(repo_path)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        # Get changed files
        changed_files = []
        recent_commits = git_analyzer.get_recent_changes(max_commits=10)
        
        for commit in recent_commits:
            for change in commit['changes']:
                if change['file'].endswith(('.java', '.py', '.js', '.ts')) and change['file'] not in changed_files:
                    changed_files.append(change['file'])
        
        # Limit files
        changed_files = changed_files[:max_files]
        
        return jsonify({
            'success': True,
            'repo_path': repo_path,
            'files_found': len(changed_files),
            'files': changed_files,
            'commits_analyzed': len(recent_commits),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Impact Analysis Endpoints
# ============================================================================

@app.route(f'{API_PREFIX}/impact', methods=['POST'])
def impact_analysis():
    """
    Perform impact analysis on a file
    
    Request Body:
        {
            "file_path": "string (required)",
            "repo_path": "string (optional, default: current directory)"
        }
    
    Returns:
        200: Impact analysis result
        400: Bad request
        500: Internal error
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify({'error': 'file_path is required'}), 400
        
        file_path = data['file_path']
        repo_path = data.get('repo_path', '.')
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Get Git changes
        try:
            git_analyzer = GitAnalyzer(repo_path)
            git_changes = git_analyzer.get_recent_changes(file_path=file_path, max_commits=5)
        except:
            git_changes = []
        
        # Perform analysis
        client = OllamaClient()
        
        # 1. Code Analysis
        code_analysis_prompt = get_java_analysis_prompt(file_path, code)
        code_analysis = client.generate_response(code_analysis_prompt)
        
        # 2. Impact Analysis
        impact_prompt = get_impact_analysis_prompt(file_path, code, git_changes)
        impact_result = client.generate_response(impact_prompt)
        
        # 3. Quality Report
        quality_prompt = get_quality_report_prompt(file_path, code, code_analysis, impact_result)
        quality_report = client.generate_response(quality_prompt)
        
        # Save reports
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.basename(file_path).replace('.java', '').replace('.py', '').replace('.js', '')
        
        reports = {}
        for report_type, content in [
            ('code_analysis', code_analysis),
            ('impact_analysis', impact_result),
            ('quality_report', quality_report)
        ]:
            report_id = f"{base_name}_{report_type}_{timestamp}.md"
            report_path = os.path.join(REPORTS_DIR, report_id)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            reports[report_type] = report_id
        
        return jsonify({
            'success': True,
            'file_path': file_path,
            'code_analysis': code_analysis,
            'impact_analysis': impact_result,
            'quality_report': quality_report,
            'reports': reports,
            'git_commits_analyzed': len(git_changes),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Reports Management Endpoints
# ============================================================================

@app.route(f'{API_PREFIX}/reports', methods=['GET'])
def list_reports():
    """
    List all generated reports
    
    Query Parameters:
        type: Filter by report type (optional)
        limit: Maximum number of reports (optional, default: 50)
    
    Returns:
        200: List of reports
    """
    try:
        report_type = request.args.get('type')
        limit = int(request.args.get('limit', 50))
        
        reports = []
        for root, dirs, files in os.walk(REPORTS_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    stat = os.stat(file_path)
                    
                    # Determine type
                    if 'quality_report' in file:
                        rtype = 'quality'
                    elif 'impact' in file:
                        rtype = 'impact'
                    else:
                        rtype = 'analysis'
                    
                    # Filter by type if specified
                    if report_type and rtype != report_type:
                        continue
                    
                    reports.append({
                        'id': file,
                        'type': rtype,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'path': os.path.relpath(file_path, REPORTS_DIR)
                    })
        
        # Sort by creation time (newest first)
        reports.sort(key=lambda x: x['created'], reverse=True)
        
        # Limit results
        reports = reports[:limit]
        
        return jsonify({
            'success': True,
            'total': len(reports),
            'reports': reports,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route(f'{API_PREFIX}/reports/<report_id>', methods=['GET'])
def get_report(report_id):
    """
    Get a specific report
    
    Returns:
        200: Report content
        404: Report not found
    """
    try:
        report_path = os.path.join(REPORTS_DIR, report_id)
        
        if not os.path.exists(report_path):
            return jsonify({'error': 'Report not found'}), 404
        
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'id': report_id,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route(f'{API_PREFIX}/reports/<report_id>', methods=['DELETE'])
def delete_report(report_id):
    """
    Delete a specific report
    
    Returns:
        200: Report deleted
        404: Report not found
    """
    try:
        report_path = os.path.join(REPORTS_DIR, report_id)
        
        if not os.path.exists(report_path):
            return jsonify({'error': 'Report not found'}), 404
        
        os.remove(report_path)
        
        return jsonify({
            'success': True,
            'message': 'Report deleted',
            'id': report_id,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Code Analyzer REST API")
    print("=" * 60)
    print(f"API Version: {API_VERSION}")
    print(f"Reports directory: {REPORTS_DIR}")
    print(f"API Base URL: http://localhost:8000{API_PREFIX}")
    print("=" * 60)
    print("\nAvailable Endpoints:")
    print(f"  GET  {API_PREFIX}/health")
    print(f"  GET  {API_PREFIX}/status")
    print(f"  POST {API_PREFIX}/analyze")
    print(f"  POST {API_PREFIX}/analyze/file")
    print(f"  POST {API_PREFIX}/analyze/repo")
    print(f"  POST {API_PREFIX}/impact")
    print(f"  GET  {API_PREFIX}/reports")
    print(f"  GET  {API_PREFIX}/reports/<id>")
    print(f"  DEL  {API_PREFIX}/reports/<id>")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=8000)
