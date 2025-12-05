def get_knowledge_graph_prompt(content):
    """
    Generates a prompt for extracting Knowledge Graph entities and relationships.
    """
    return f"""
    You are an expert in Knowledge Graphs and Data Modeling. Your task is to analyze the provided content and extract structured information to build a Knowledge Graph.

    Content:
    ```
    {content}
    ```

    Please identify:
    1. **Entities**: Key objects, concepts, or components (e.g., Classes, Methods, Variables, Technologies).
    2. **Relationships**: How these entities interact or relate to each other (e.g., 'calls', 'inherits', 'uses', 'defines').

    Output the result in a structured format (e.g., JSON or a list of triples) like:
    - Entity: [Name] (Type: [Type])
    - Relationship: [Entity A] --[Predicate]--> [Entity B]

    Ensure the output is concise and focuses on the most important connections.
    """
