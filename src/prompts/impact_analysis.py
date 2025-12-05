def get_impact_analysis_prompt(file_path, code_content, git_changes):
    """
    Generates a prompt for analyzing the impact of code changes.
    
    Args:
        file_path: Path to the file being analyzed
        code_content: Current content of the file
        git_changes: List of recent git commits and changes
    """
    
    # Format git changes
    changes_text = ""
    if git_changes:
        changes_text = "### Recent Changes:\n\n"
        for commit in git_changes:
            changes_text += f"**Commit {commit['hash']}** by {commit['author']} on {commit['date']}\n"
            changes_text += f"Message: {commit['message']}\n"
            if commit['changes']:
                for change in commit['changes']:
                    changes_text += f"  - {change['file']}: {change['change_type']} "
                    changes_text += f"(+{change['additions']} -{change['deletions']})\n"
            changes_text += "\n"
    else:
        changes_text = "No recent changes found in git history.\n"
    
    return f"""
    You are an expert software architect and code reviewer specializing in impact analysis.
    
    File: {file_path}
    
    {changes_text}
    
    Current Code:
    ```java
    {code_content}
    ```
    
    Please provide a comprehensive **Impact Analysis** covering:
    
    1. **Change Summary**
       - What was changed in recent commits?
       - What is the scope of these changes?
    
    2. **Impact Assessment**
       - Which components/modules are affected by these changes?
       - Are there any breaking changes?
       - What are the potential risks?
    
    3. **Dependencies & Side Effects**
       - What other parts of the codebase might be impacted?
       - Are there any API changes that affect consumers?
       - Database schema or configuration changes?
    
    4. **Quality & Risk Analysis**
       - Code quality improvements or degradations
       - Security implications
       - Performance impact
       - Test coverage considerations
    
    5. **Recommendations**
       - What additional testing is needed?
       - Are there any refactoring opportunities?
       - Suggested next steps
    
    Output the result in a structured Markdown format suitable for a quality report.
    """


def get_quality_report_prompt(file_path, code_content, analysis_results, impact_analysis):
    """
    Generates a prompt for creating a comprehensive quality report.
    
    Args:
        file_path: Path to the file
        code_content: Current code content
        analysis_results: Previous code analysis results
        impact_analysis: Impact analysis results
    """
    return f"""
    You are a senior quality assurance engineer. Generate a comprehensive **Code Quality Report**.
    
    File: {file_path}
    
    Code Analysis:
    {analysis_results}
    
    Impact Analysis:
    {impact_analysis}
    
    Please create a **Quality Report** with the following sections:
    
    # Code Quality Report: {file_path}
    
    ## Executive Summary
    - Overall quality score (1-10)
    - Critical issues count
    - Change risk level (Low/Medium/High)
    
    ## Code Metrics
    - Code complexity
    - Maintainability index
    - Technical debt indicators
    
    ## Issues & Findings
    ### Critical Issues
    - List critical bugs or security vulnerabilities
    
    ### Warnings
    - List potential problems
    
    ### Suggestions
    - List improvement opportunities
    
    ## Change Impact Summary
    - Summary of recent changes
    - Affected components
    - Risk assessment
    
    ## Testing Recommendations
    - Required test coverage
    - Suggested test scenarios
    - Regression testing needs
    
    ## Action Items
    - Prioritized list of recommended actions
    - Estimated effort for each item
    
    ## Conclusion
    - Overall assessment
    - Go/No-Go recommendation for deployment
    
    Format the output as a professional Markdown report.
    """
