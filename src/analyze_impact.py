import os
import sys

# Add the src directory to the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm.ollama_client import OllamaClient
from llm.git_analyzer import GitAnalyzer
from prompts.java_analysis import get_java_analysis_prompt
from prompts.impact_analysis import get_impact_analysis_prompt, get_quality_report_prompt

def analyze_with_impact(repo_path, output_dir=None):
    """
    Analyze Java files with Git change impact analysis.
    
    Args:
        repo_path: Path to the git repository
        output_dir: Optional path to save reports
    """
    
    # Initialize Git Analyzer
    try:
        git_analyzer = GitAnalyzer(repo_path)
        print(f"✓ Git repository detected: {repo_path}\n")
    except ValueError as e:
        print(f"Error: {e}")
        print("This tool requires a git repository. Initialize git first with: git init")
        return
    
    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        quality_report_dir = os.path.join(output_dir, "quality_reports")
        os.makedirs(quality_report_dir, exist_ok=True)
        print(f"Reports will be saved to: {output_dir}\n")
    
    # Get changed Java files from recent commits
    changed_files = []
    recent_commits = git_analyzer.get_recent_changes(max_commits=10)
    
    for commit in recent_commits:
        for change in commit['changes']:
            if change['file'].endswith('.java') and change['file'] not in changed_files:
                changed_files.append(change['file'])
    
    if not changed_files:
        print("No Java files found in recent commits. Scanning all Java files...")
        # Fallback to scanning all Java files
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.java'):
                    rel_path = os.path.relpath(os.path.join(root, file), repo_path)
                    changed_files.append(rel_path)
    
    if not changed_files:
        print("No Java files found.")
        return
    
    print(f"Found {len(changed_files)} Java file(s) to analyze.\n")
    
    # Initialize Ollama Client
    client = OllamaClient()
    
    for file_path in changed_files:
        full_path = os.path.join(repo_path, file_path)
        
        if not os.path.exists(full_path):
            print(f"⚠ File not found: {file_path} (may have been deleted)")
            continue
        
        print(f"{'='*60}")
        print(f"Analyzing: {file_path}")
        print(f"{'='*60}\n")
        
        try:
            # Read file content
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get git changes for this file
            git_changes = git_analyzer.get_recent_changes(file_path=file_path, max_commits=5)
            
            # 1. Basic Code Analysis
            print("📊 Step 1/3: Code Analysis...")
            code_analysis_prompt = get_java_analysis_prompt(file_path, content)
            code_analysis = client.generate_response(code_analysis_prompt)
            
            # 2. Impact Analysis
            print("🔍 Step 2/3: Impact Analysis...")
            impact_prompt = get_impact_analysis_prompt(file_path, content, git_changes)
            impact_analysis = client.generate_response(impact_prompt)
            
            # 3. Quality Report Generation
            print("📝 Step 3/3: Generating Quality Report...")
            quality_prompt = get_quality_report_prompt(file_path, content, code_analysis, impact_analysis)
            quality_report = client.generate_response(quality_prompt)
            
            # Display results
            print("\n" + "="*60)
            print("QUALITY REPORT")
            print("="*60)
            print(quality_report)
            print("\n")
            
            # Save to files if output directory is specified
            if output_dir:
                base_name = os.path.basename(file_path).replace('.java', '')
                
                # Save code analysis
                analysis_path = os.path.join(output_dir, f"{base_name}_analysis.md")
                with open(analysis_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Code Analysis: {file_path}\n\n")
                    f.write(code_analysis)
                
                # Save impact analysis
                impact_path = os.path.join(output_dir, f"{base_name}_impact.md")
                with open(impact_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Impact Analysis: {file_path}\n\n")
                    f.write(impact_analysis)
                
                # Save quality report
                report_path = os.path.join(quality_report_dir, f"{base_name}_quality_report.md")
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(quality_report)
                
                print(f"✓ Saved reports:")
                print(f"  - Code Analysis: {analysis_path}")
                print(f"  - Impact Analysis: {impact_path}")
                print(f"  - Quality Report: {report_path}")
                print()
        
        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}\n")
    
    print("\n" + "="*60)
    print("Analysis Complete!")
    print("="*60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 src/analyze_impact.py <repository_path> [output_directory]")
        print()
        print("  repository_path: Path to git repository containing Java files")
        print("  output_directory: (Optional) Path to save analysis reports")
        print()
        print("Example:")
        print("  python3 src/analyze_impact.py . reports/")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    analyze_with_impact(repo_path, output_dir)
