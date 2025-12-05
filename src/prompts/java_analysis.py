def get_java_analysis_prompt(file_path, code_content):
    """
    Generates the prompt for analyzing Java code.
    """
    return f"""
    You are an expert Java developer and code reviewer. Please analyze the following Java code.
    
    File: {file_path}
    
    Code:
    ```java
    {code_content}
    ```
    
    Please provide a concise analysis covering:
    1. Functionality summary (What does this code do?)
    2. Potential bugs or issues (if any)
    3. Improvement suggestions (refactoring, performance, style)
    
    Output the result in Markdown format.
    """
