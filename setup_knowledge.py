# setup_knowledge.py
from agents.retriever import setup_retriever
from dotenv import load_dotenv

load_dotenv()

# ACTUAL PROJECT FOLDER
target_folder = "/Users/maliha/Desktop/code-smells-python-main/command-line-shell/before" 

if __name__ == "__main__":
    # If folder not found, create a dummy one for testing:
    import os
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        with open(f"{target_folder}/auth.py", "w") as f:
            f.write("def login(user): return True # Legacy login function")
            
    setup_retriever(target_folder)
