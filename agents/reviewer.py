# agents/reviewer.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from state import AgentState

# Define the Prompt
REVIEW_PROMPT = """
You are a Senior Software Engineer at Meta. You are reviewing a PR that contains AI-generated code.
Your goal is to ensure correctness, maintainability, and consistency.

### TARGET
- Project folder: {project_folder}
- File name: {file_name}

### INPUT DATA
1. **The Code Change:**
{code_content}

2. **Automated Analysis (Radon):**
- Complexity Score: {complexity_score} (Threshold: 10)
- Analyst Verdict: {analyst_verdict}
- Raw Metrics: {raw_metrics}

3. **Project Context (Retrieved History):**
{related_context}

### INSTRUCTIONS
- If Analyst Verdict is FAIL, you MUST request changes. Cite the complexity score.
- Check the 'Project Context'. Does the new code use existing patterns? (e.g. correct logging, auth wrappers).
- Look for "Hallucinations": Are there imports or function calls that look plausible but don't match the Context?

### OUTPUT FORMAT
Provide a structured review in Markdown:
**Status:** [APPROVE / REQUEST_CHANGES]
**Summary:** ...
**Critical Issues:**
- ...
**Suggestions:**
- ...
"""

def run_reviewer(state: AgentState) -> AgentState:
    """
    Reviewer Node: The LLM that synthesizes all data into a final review.
    """
    print("--- Reviewer Agent: Generating Final Review ---")
    
    # Initialize LLM (GPT-4o or GPT-3.5-turbo)
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # Create Chain
    prompt = ChatPromptTemplate.from_template(REVIEW_PROMPT)
    chain = prompt | llm
    
    # Execute
    response = chain.invoke({
        "code_content": state["code_content"],
        "complexity_score": state["complexity_score"],
        "analyst_verdict": state["analyst_verdict"],
        "raw_metrics": state["raw_metrics"],
        "related_context": state.get("related_context", "No context found."),
        "file_name": state.get("file_name", "unknown"),
        "project_folder": state.get("project_folder", "unknown"),
    })
    
    return {
        "final_decision": "COMPLETED",
        "review_comments": [response.content]
    }
