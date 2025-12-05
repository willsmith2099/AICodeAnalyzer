import os
import sys

# Add the src directory to the python path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm.ollama_client import OllamaClient
from prompts.java_analysis import get_java_analysis_prompt

def process_directory(directory_path, output_dir=None):
    """
    Recursively finds all .java files in the directory and analyzes them.
    
    Args:
        directory_path: Path to the directory containing Java files
        output_dir: Optional path to save analysis results. If None, only prints to console.
    """
    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return

    print(f"Scanning directory: {directory_path}...\n")
    
    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        print(f"Analysis results will be saved to: {output_dir}\n")
    
    java_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    
    if not java_files:
        print("No .java files found.")
        return

    print(f"Found {len(java_files)} Java files. Starting analysis...\n")
    
    # Initialize Ollama Client
    client = OllamaClient()
    
    for file_path in java_files:
        print(f"--- Analyzing {file_path} ---")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate Prompt
            prompt = get_java_analysis_prompt(file_path, content)
            
            # Get Response
            analysis = client.generate_response(prompt)
            print(analysis)
            print("\n" + "="*50 + "\n")
            
            # Save to file if output directory is specified
            if output_dir:
                # Create output filename based on input filename
                base_name = os.path.basename(file_path)
                output_filename = base_name.replace('.java', '_analysis.md')
                output_path = os.path.join(output_dir, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as out_file:
                    out_file.write(f"# Analysis of {file_path}\n\n")
                    out_file.write(analysis)
                    out_file.write("\n")
                
                print(f"✓ Saved analysis to: {output_path}\n")
            
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 src/analyze_java.py <directory_path> [output_directory]")
        print("  directory_path: Path to Java project directory")
        print("  output_directory: (Optional) Path to save analysis results")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    process_directory(target_dir, output_dir)
