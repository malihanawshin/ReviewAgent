# agents/retriever.py
from langchain_community.document_loaders import PythonLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_chroma import Chroma 
#from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from state import AgentState

DB_PATH = "./data/chroma_db"

def setup_retriever(folder_path: str):
    print(f"--- Retriever: Indexing folder '{folder_path}' ---")
    
    #loader = DirectoryLoader(folder_path, glob="**/*.py", loader_cls=PythonLoader)
    loader = DirectoryLoader(
    folder_path, 
    glob="**/*.py", 
    loader_cls=PythonLoader,
    exclude=["**/site-packages/**", "**/.venv/**", "**/node_modules/**"] # Safety filter
    )

    docs = loader.load()
    
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON,
        chunk_size=1000, 
        chunk_overlap=200
    )
    splits = splitter.split_documents(docs)
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 1. Initialize the vector store first
    vectorstore = Chroma(
        embedding_function= embeddings, #OpenAIEmbeddings(),
        persist_directory=DB_PATH
    )
    
    # 2. Add documents in batches
    # This avoids the constructor argument conflict
    vectorstore.add_documents(documents=splits)
    
    print(f"--- Indexing Complete. {len(splits)} chunks stored. ---")
    return vectorstore.as_retriever()

def run_retriever(state: AgentState) -> AgentState:
    print(f"--- Retriever: Searching context for {state.get('file_name')} ---")
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma( 
        embedding_function= embeddings, #OpenAIEmbeddings()
        persist_directory=DB_PATH
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    
    query = f"Code related to {state.get('file_name', '')} or: {state['code_content'][:200]}"
    results = retriever.invoke(query)
    
    context_str = "\n\n".join([f"--- Related File: {doc.metadata.get('source', 'Unknown')} ---\n{doc.page_content}" for doc in results])
    
    return {
        "related_context": context_str,
        # PASS THROUGH THESE KEYS so they don't get lost
        "code_content": state["code_content"],
        "file_name": state.get("file_name"),
        "complexity_score": state.get("complexity_score"),
        "analyst_verdict": state.get("analyst_verdict"),
        "raw_metrics": state.get("raw_metrics")
    }

