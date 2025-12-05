from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import sys
import markdown
from datetime import datetime
import glob

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.ollama_client import OllamaClient
from src.llm.git_analyzer import GitAnalyzer
from src.prompts.java_analysis import get_java_analysis_prompt
from src.prompts.impact_analysis import get_impact_analysis_prompt, get_quality_report_prompt

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global paths
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/reports')
def list_reports():
    """List all generated reports"""
    reports = []
    
    # Scan for all report files
    for root, dirs, files in os.walk(REPORTS_DIR):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, REPORTS_DIR)
                
                # Get file stats
                stat = os.stat(file_path)
                reports.append({
                    'name': file,
                    'path': rel_path,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'type': 'quality' if 'quality_report' in file else 'impact' if 'impact' in file else 'analysis'
                })
    
    # Sort by modified time (newest first)
    reports.sort(key=lambda x: x['modified'], reverse=True)
    
    return jsonify(reports)

@app.route('/report/<path:filename>')
def view_report(filename):
    """View a specific report"""
    file_path = os.path.join(REPORTS_DIR, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'Report not found'}), 404
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(content, extensions=['fenced_code', 'tables', 'nl2br'])
        
        return jsonify({
            'filename': filename,
            'content': content,
            'html': html_content
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_code():
    """Analyze code snippet or file"""
    data = request.json
    
    code = data.get('code', '')
    language = data.get('language', 'java')
    analysis_type = data.get('type', 'basic')  # basic or impact
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    try:
        client = OllamaClient()
        
        # Generate appropriate prompt based on language
        if language == 'java':
            prompt = get_java_analysis_prompt('snippet.java', code)
        else:
            # Generic analysis for other languages
            prompt = f"""
            You are an expert code reviewer. Analyze the following {language} code:
            
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
        
        # Convert to HTML
        html_content = markdown.markdown(analysis, extensions=['fenced_code', 'tables'])
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'html': html_content
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-repo', methods=['POST'])
def analyze_repository():
    """Analyze a Git repository"""
    data = request.json
    
    repo_path = data.get('repo_path', '.')
    
    if not os.path.exists(repo_path):
        return jsonify({'error': 'Repository path not found'}), 400
    
    try:
        # Initialize Git Analyzer
        git_analyzer = GitAnalyzer(repo_path)
        
        # Get changed files
        changed_files = []
        recent_commits = git_analyzer.get_recent_changes(max_commits=10)
        
        for commit in recent_commits:
            for change in commit['changes']:
                if change['file'].endswith(('.java', '.py', '.js')) and change['file'] not in changed_files:
                    changed_files.append(change['file'])
        
        if not changed_files:
            # Fallback to all code files
            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    if file.endswith(('.java', '.py', '.js')):
                        rel_path = os.path.relpath(os.path.join(root, file), repo_path)
                        if rel_path not in changed_files:
                            changed_files.append(rel_path)
        
        return jsonify({
            'success': True,
            'files': changed_files[:20],  # Limit to 20 files
            'total': len(changed_files)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        client = OllamaClient()
        # Simple test
        return jsonify({
            'status': 'healthy',
            'ollama': 'connected'
        })
    except:
        return jsonify({
            'status': 'unhealthy',
            'ollama': 'disconnected'
        }), 503

if __name__ == '__main__':
    print("=" * 60)
    print("Code Analyzer Web Interface")
    print("=" * 60)
    print(f"Reports directory: {REPORTS_DIR}")
    print(f"Starting server at http://localhost:5001")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5001)

