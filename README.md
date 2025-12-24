Review Agent
============

Review Agent is a prototype multi‑agent code review assistant for Python projects. It combines static analysis, repository‑level context retrieval, and an LLM reviewer to generate structured code review reports for individual files.

The system is built with LangGraph for orchestration, Radon for complexity analysis, and sentence‑transformer embeddings (all‑MiniLM‑L6‑v2) for local, free vector search over the project codebase.[1][2][3]

## Features

- Static analysis via Radon to compute cyclomatic complexity and basic raw metrics for each reviewed file.[2][4]
- Repository‑aware context: indexes a project folder and retrieves related code snippets when reviewing a file.[5][6]
- LLM‑based reviewer that combines:
  - the target file,
  - static metrics (complexity, lines of code),
  - retrieved project context,
  into a single structured review (status, summary, critical issues, suggestions).[7][1]
- Reviews are saved as Markdown files under `reviews/` for later inspection.  
- Swappable embedding backend: uses Hugging Face sentence‑transformers locally (no API key required) for embeddings.[3][8]

## Architecture

The system is organized as a simple LangGraph workflow with three main agents:

- Analyst  
  - Uses Radon programmatically to compute cyclomatic complexity and raw metrics.  
  - Produces a verdict (PASS/FAIL) based on a configurable complexity threshold.[9][2]

- Retriever  
  - Indexes all `.py` files in a target project folder into a Chroma vector store using all‑MiniLM‑L6‑v2 embeddings.[6][3]
  - For a given file under review, retrieves the most relevant code chunks as project context (e.g., related helpers, classes, or modules).  

- Reviewer  
  - A chat‑style LLM agent (e.g., OpenAI or another provider) orchestrated via LangChain/LangGraph.[10][1]
  - Generates a Markdown review that includes status, summary, critical issues, and suggestions, taking into account both static metrics and retrieved context.

State is passed along the graph as a shared dictionary (code content, file name, complexity score, raw metrics, retrieved context, and final review text).

## Installation

1. Clone the repository and create a virtual environment:

```bash
git clone https://github.com/malihanawshin/ReviewAgent.git
cd review-agent
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Typical dependencies include:

- `langgraph`, `langchain` for agent orchestration.
- `radon` for code metrics.[11]
- `langchain-chroma` and `chromadb` for vector storage.[6]
- `langchain-huggingface` and `sentence-transformers` for local embeddings with `all-MiniLM-L6-v2`.[3][5]
- An LLM client library (e.g., `langchain-openai`) if using an external model.

3. Environment variables:

Create a `.env` file in the project root:

```env
# Only needed if you use a remote LLM provider
OPENAI_API_KEY=your_api_key_here
```

If you use only local embeddings and a local or mock LLM, no Hugging Face key is required.

## Usage

### 1. Index a project (repository context)

Point `setup_knowledge.py` to the project folder you want the agent to know about:

```python
# setup_knowledge.py
target_folder = "/absolute/path/to/your/python/project"
```

Run:

```bash
python setup_knowledge.py
```

This will:

- Load all `.py` files (optionally excluding virtualenvs and `node_modules`).  
- Split them into chunks using `RecursiveCharacterTextSplitter`.  
- Embed and store them in a persistent Chroma database under `data/chroma_db`.[5][6]

If you later switch to a different project, delete the old index first:

```bash
rm -rf data/chroma_db
python setup_knowledge.py
```

### 2. Run a review for a specific file

In `main.py`, set the path to the file you want to review:

```python
target_file = "/absolute/path/to/your/python/project/some_module.py"
```

Then run:

```bash
python main.py
```

The pipeline will:

- Run the Analyst agent (Radon) on `target_file`.  
- Retrieve relevant context from the indexed project.  
- Ask the Reviewer agent to generate a Markdown review.  
- Print the review in the terminal and save it to `reviews/review_YYYYMMDD_HHMMSS.md`.

## Customization

- Complexity threshold: Adjust the `COMPLEXITY_THRESHOLD` constant in the Analyst agent to tune when the review should automatically flag complexity issues.
- Embedding model: Swap `all-MiniLM-L6-v2` for another sentence‑transformer model if you need higher quality or different performance characteristics.
- LLM provider: Replace the Reviewer’s LLM client (e.g., use Groq, Anthropic, or a local model) by editing `agents/reviewer.py`.  
- Output format: Modify the prompt and saving logic to include additional metadata such as project name, file path, or commit hash.

## Limitations

- The current implementation focuses on Python and uses simple heuristics around complexity and context; it is not a replacement for a full CI code review system.
- Repository context is rebuilt per project; switching between projects requires rebuilding the Chroma index.  
- Quality of the final review depends heavily on the chosen LLM and the amount of meaningful context available in the indexed project.

## License

MIT License. Open for research and educational use.

[1](https://github.com/aws-samples/langgraph-multi-agent)
[2](https://pypi.org/project/radon/0.4/)
[3](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[4](https://www.blog.pythonlibrary.org/2023/09/20/learning-about-code-metrics-in-python-with-radon/)
[5](https://docs.langchain.com/oss/python/integrations/text_embedding/sentence_transformers)
[6](https://docs.langchain.com/oss/python/integrations/vectorstores/chroma)
[7](https://github.com/botextractai/ai-langgraph-multi-agent)
[8](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html)
[9](https://radon.readthedocs.io/en/latest/api.html)
[10](https://github.com/langchain-ai/langgraph/blob/main/examples/multi_agent/multi-agent-collaboration.ipynb)
[11](https://github.com/rubik/radon)
