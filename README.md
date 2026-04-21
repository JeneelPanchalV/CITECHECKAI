# DocGuard AI a.k.a CiteCheck AI

**Evidence-Grounded PDF Question Answering with Citations and Hallucination Prevention**

DocGuard AI is a fully local, privacy-safe RAG (Retrieval-Augmented Generation) system that answers questions strictly from uploaded PDF documents. Every answer is grounded in retrieved evidence and includes page-level citations. When evidence is insufficient, the system refuses to answer rather than hallucinate.

---

## Features

- **Evidence-grounded answers** — responses are generated only from retrieved document chunks
- **Page-level citations** — every answer references the exact page it came from
- **Hallucination guard** — refuses to answer when semantic similarity is too weak or evidence is insufficient
- **Fully local** — runs entirely on your machine with no cloud APIs or data sharing
- **Privacy-safe** — your documents never leave your device
- **Transparent retrieval** — users can inspect retrieved chunks, similarity scores, and source snippets

---

## System Architecture

```
User Query
    │
    ▼
Streamlit UI
    │
    ▼
PDF Upload + Storage
    │
    ▼
PDF Loader (pypdf)
    │
    ▼
Chunking Engine (page-aware)
    │
    ▼
Embedding Model (all-MiniLM-L6-v2)
    │
    ▼
Vector Database (ChromaDB)
    │
    ▼
Hallucination Guard (evidence validation)
    │         │
    │    [weak evidence]
    │         │
    │         ▼
    │    Refuse Answer
    │
    ▼
LLM Generation (Ollama / llama3.1:8b)
    │
    ▼
Answer + Page Citations
```

---

## Tech Stack

| Component        | Technology                          |
|------------------|-------------------------------------|
| UI               | Streamlit                           |
| PDF Parsing      | pypdf                               |
| Embeddings       | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Database  | ChromaDB (persistent local storage) |
| LLM Runtime      | Ollama (llama3.1:8b)                |
| Language         | Python 3.10                         |
| Environment      | Conda                               |

---

## Project Structure

```
DocGuardAI/
├── app/
│   └── main.py              # Streamlit UI
├── core/
│   ├── config.py            # Environment config
│   ├── pdf_loader.py        # Page-aware PDF text extraction
│   ├── chunking.py          # Overlapping chunk generation
│   ├── embeddings.py        # Local embedding model
│   ├── vector_store.py      # ChromaDB storage and retrieval
│   ├── guard.py             # Hallucination detection logic
│   ├── llm_ollama.py        # Ollama LLM interface
│   └── rag.py               # Full RAG pipeline
├── storage/
│   ├── uploads/             # Uploaded PDF files
│   └── chroma/              # Persistent vector index
├── .env                     # Environment variables
├── .gitignore
└── README.md
```

---

## Prerequisites

- macOS (Apple Silicon M1/M2/M3 recommended)
- [Ollama](https://ollama.com) installed system-wide
- Conda or Python 3.10+

---

## Installation

### 1. Install Ollama and pull the model

```bash
brew install ollama
ollama serve
```

In a new terminal:

```bash
ollama pull llama3.1:8b
```

### 2. Create and activate conda environment

```bash
conda create -n docguard-ai python=3.10 -y
conda activate docguard-ai
```

### 3. Install dependencies

```bash
pip install streamlit pypdf chromadb sentence-transformers requests python-dotenv
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
EMBED_MODEL=all-MiniLM-L6-v2
CHROMA_DIR=storage/chroma
UPLOAD_DIR=storage/uploads
```

---

## Running the App

Make sure Ollama is running in a separate terminal:

```bash
ollama serve
```

Then launch the Streamlit app:

```bash
conda activate docguard-ai
python -m streamlit run app/main.py
```

Open your browser at `http://localhost:8501`.

---

## Usage

1. **Upload a PDF** using the sidebar file uploader
2. Click **Index PDF** to extract, chunk, embed, and store the document
3. Enter a question in the text input field
4. Click **Ask** to retrieve evidence and generate a grounded answer
5. View the **answer**, **hallucination guard status**, and **evidence snippets** with page numbers

---

## Hallucination Guard

The guard validates retrieved evidence before any LLM call using three checks:

| Check                  | Threshold         | Description                              |
|------------------------|-------------------|------------------------------------------|
| Best match distance    | < 1.4             | Top retrieved chunk must be close enough |
| Average distance       | < 1.8             | Overall evidence must be relevant        |
| Total evidence length  | ≥ 600 characters  | Enough text to support an answer         |

If any check fails, the system returns:

```
Insufficient evidence in the provided document.
```

No LLM call is made.

---

## Example

**Question:**
```
What is DocGuard AI?
```

**Answer:**
```
DocGuard AI is a system for evidence-grounded PDF question answering 
with citations and hallucination prevention, designed for 
privacy-sensitive use cases. [1]
```

**Evidence:**
```
[1] DocGuard_AI.pdf, Page 1 (distance=0.974)
DocGuard AI is a local-first RAG system that answers questions...
```

**Guard Status:** ✅ OK

---

## Configuration

You can tune chunking and guard behaviour via `.env` or directly in the relevant modules:

| Parameter       | Default | Location          | Description                        |
|-----------------|---------|-------------------|------------------------------------|
| `chunk_size`    | 800     | `chunking.py`     | Words per chunk                    |
| `overlap`       | 120     | `chunking.py`     | Overlapping words between chunks   |
| `top_k`         | 5       | `rag.py`          | Number of chunks retrieved         |
| `temperature`   | 0.1     | `llm_ollama.py`   | LLM generation temperature         |
| `best distance` | 1.4     | `guard.py`        | Max allowed top-match distance     |
| `avg distance`  | 1.8     | `guard.py`        | Max allowed average distance       |
| `min chars`     | 600     | `guard.py`        | Minimum evidence character count   |

---

## Limitations

- Scanned PDFs (image-based) are not supported — text extraction requires selectable text
- Single document indexing per session (multi-PDF support planned)
- Response speed depends on available RAM and Apple Silicon GPU availability

---

## Roadmap

- [ ] Multi-PDF support with document name in citations
- [ ] OCR support for scanned PDFs
- [ ] Answer confidence scoring
- [ ] Document text highlighting for cited passages
- [ ] Retrieval evaluation metrics (MRR, NDCG)
- [ ] Deployment packaging (Docker / standalone app)

---

## License

This project is licensed under the MIT License.

---

## Acknowledgements

- [Ollama](https://ollama.com) — local LLM runtime
- [ChromaDB](https://www.trychroma.com) — vector database
- [sentence-transformers](https://www.sbert.net) — embedding model
- [Streamlit](https://streamlit.io) — UI framework
- [pypdf](https://pypdf.readthedocs.io) — PDF text extraction