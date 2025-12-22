# state.py
from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    """
    The shared memory passed between agents.
    """
    # INPUT
    code_content: str          # The code snippet/diff to review
    file_name: str             # Context: filename (e.g., 'auth.py')
    
    # ANALYST AGENT OUTPUTS
    complexity_score: int      # Max Cyclomatic Complexity (CC)
    raw_metrics: dict          # LOC, comments, etc.
    analyst_verdict: str       # "PASS" or "FAIL" based on complexity
    
    # REVIEWER AGENT OUTPUTS
    review_comments: List[str] # List of semantic issues found
    final_decision: str        # "APPROVE" or "REQUEST_CHANGES"

    related_context: str
