# main.py
from langgraph.graph import StateGraph, START, END
from agents.analyst import run_analyst
from agents.retriever import run_retriever
from agents.reviewer import run_reviewer
from state import AgentState
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

def build_graph():
    # 1. Initialize Graph
    workflow = StateGraph(AgentState)
    
    # 2. Add Nodes (Agents)
    workflow.add_node("analyst", run_analyst)
    workflow.add_node("retriever", run_retriever)
    workflow.add_node("reviewer", run_reviewer)
    
    # 3. Define Edges (The Logic Flow)
    # Start -> Analyst -> Retriever -> Reviewer -> End
    workflow.add_edge(START, "analyst")
    workflow.add_edge("analyst", "retriever")
    workflow.add_edge("retriever", "reviewer")
    workflow.add_edge("reviewer", END)
    
    return workflow.compile()

if __name__ == "__main__":
    app = build_graph()
    
    # 1. Pick a real file to review
    target_file = "/Users/maliha/Desktop/code-smells-python-main/command-line-shell/before/src/main.py"
    project_folder = os.path.dirname(target_file) 
    
    with open(target_file, "r") as f:
        real_code = f.read()
        
    print(f"\nStarting Review for {target_file}...\n")
    
    # 2. Feed it to the agent
    inputs = {
        "code_content": real_code, 
        "file_name": os.path.basename(target_file),
        "project_folder": project_folder,
    }
    
    # Run the graph
    result = app.invoke(inputs)
    
    print("\n\n================ FINAL REVIEW REPORT ================\n")
    print(result["review_comments"][-1])
    print("\n=====================================================")

    review_text = result["review_comments"][-1]

    header = f"# Review\n\n- Project: {project_folder}\n- File: {os.path.basename(target_file)}\n\n---\n\n"
    full_text = header + review_text

    # 1) folder and filename
    os.makedirs("reviews", exist_ok=True)  # creates /reviews if missing
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"reviews/review_{timestamp}.md"   # or .txt

    # 2) Write to file (UTF‑8)
    with open(file_name, "w", encoding="utf-8") as f:  # [web:148][web:145]
        f.write(full_text)

    print(f"\nReview saved to: {file_name}")



# if __name__ == "__main__":
#     app = build_graph()
    
#     # --- TEST CASE: A mix of bad complexity + potential hallucination ---
#     test_code = textwrap.dedent("""
#     def process_data(data):
#         # This looks complex...
#         if data:
#             for i in data:
#                 if i > 5:
#                     print('high')
#                     if i > 100:
#                         # Potential Hallucination: Is 'utils.super_log' real?
#                         import utils 
#                         utils.super_log(i) 
#                 else:
#                     print('low')
#         return True
#     """)
    
#     print("\n Starting ReviewAgent Pipeline...\n")
#     inputs = {"code_content": test_code, "file_name": "processor.py"}
    
    


# test_analyst.py
# from agents.analyst import run_analyst
# from state import AgentState

# # 1. Test with Good Code
# good_code = """
# def add(a, b):
#     return a + b
# """
# print("\nTesting GOOD Code:")
# state_good = AgentState(code_content=good_code, file_name="math_utils.py")
# result_good = run_analyst(state_good)
# print(f"Verdict: {result_good['analyst_verdict']}")
# print(f"Score: {result_good['complexity_score']}")

# # 2. Test with Complex Code (Spaghetti)
# bad_code = """
# def chaotic_function(data, mode, threshold):
#     results = []
#     if mode == 'strict':
#         for item in data:
#             if item > threshold:
#                 if item % 2 == 0:
#                     results.append(item / 2)
#                 else:
#                     results.append(item * 3 + 1)
#             elif item < 0:
#                 try:
#                     if abs(item) > threshold:
#                         results.append(0)
#                     else:
#                         raise ValueError("Too small")
#                 except ValueError:
#                     pass
#             else:
#                 continue
#     elif mode == 'loose':
#         while len(results) < 5:
#             if not data:
#                 break
#             val = data.pop()
#             if val:
#                 results.append(val)
#             elif val is None:
#                 continue
#             else:
#                 return []
#     else:
#         if threshold < 10:
#             return None
#         elif threshold > 100:
#             return "Too high"
            
#     return results
# """


# print("\nTesting BAD Code:")
# state_bad = AgentState(code_content=bad_code, file_name="legacy.py")
# result_bad = run_analyst(state_bad)
# print(f"Verdict: {result_bad['analyst_verdict']}")
# print(f"Score: {result_bad['complexity_score']} (Should be > 10)")


# import radon.complexity as radon_cc
# from langgraph.graph import StateGraph, START, END
# from typing import TypedDict, List

# # 1. Test Radon (The Analyst)
# code_sample = """
# def factorial(n):
#     if n < 2: return 1
#     return n * factorial(n-1)
# """
# try:
#     results = radon_cc.cc_visit(code_sample)
#     print(f"Radon Installed. Complexity of sample: {results[0].complexity}")
# except Exception as e:
#     print(f"Radon Error: {e}")

# # 2. Test LangGraph (The Orchestrator)
# class State(TypedDict):
#     messages: List[str]

# def simple_node(state: State):
#     return {"messages": ["Agent is active"]}

# workflow = StateGraph(State)
# workflow.add_node("agent", simple_node)
# workflow.add_edge(START, "agent")
# workflow.add_edge("agent", END)
# app = workflow.compile()

# try:
#     res = app.invoke({"messages": []})
#     print(f"LangGraph Installed. Output: {res['messages'][0]}")
# except Exception as e:
#     print(f"LangGraph Error: {e}")
