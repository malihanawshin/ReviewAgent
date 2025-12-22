# agents/analyst.py
import radon.complexity as radon_cc
import radon.raw as radon_raw
from state import AgentState

# Research threshold: CC > 10 is generally considered "complex"
COMPLEXITY_THRESHOLD = 10

def run_analyst(state: AgentState) -> AgentState:
    """
    Analyst Node: Performs static analysis on the code.
    Does NOT use an LLM. Uses deterministic algorithms (Radon).
    """
    code = state["code_content"]
    
    print(f"--- Analyst Agent: Scanning {state.get('file_name', 'code')} ---")
    
    try:
        # 1. Calculate Cyclomatic Complexity (CC)
        # blocks are functions/classes. We get the complexity of each.
        blocks = radon_cc.cc_visit(code)
        
        # If no functions found (e.g., just imports), complexity is 1
        max_cc = max([b.complexity for b in blocks]) if blocks else 1
        
        # 2. Get Raw Metrics (Lines of Code, Comments)
        raw = radon_raw.analyze(code)
        
        # 3. Formulate Verdict
        if max_cc > COMPLEXITY_THRESHOLD:
            verdict = "FAIL"
            report = (f"REJECT: Max Complexity is {max_cc} (Limit: {COMPLEXITY_THRESHOLD}). "
                      f"Refactor '{blocks[0].name}' to reduce nesting.")
        else:
            verdict = "PASS"
            report = f"PASS: Complexity {max_cc} is within limits."

        # Return updated state
        return {
            "complexity_score": max_cc,
            "raw_metrics": {"loc": raw.loc, "sloc": raw.sloc},
            "analyst_verdict": verdict,
            "review_comments": [report] # Pre-fill comments with data
        }

    except SyntaxError as e:
        return {
            "complexity_score": -1,
            "analyst_verdict": "FAIL",
            "review_comments": [f" CRITICAL: Syntax Error - {str(e)}"]
        }
