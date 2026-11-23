# Dark Souls 2 Local RAG Assistant

A fully local **Retrieval-Augmented Generation (RAG)** pipeline built to answer questions about *Dark Souls 2* directly from Fextralife wiki data, with **zero external API costs** and strict anti-hallucination guardrails.

---

## Architecture

The pipeline runs 100% locally by decoupling embedding generation from LLM inference:

```text
[Dark Souls 2 Wiki (Fextralife)]
        |
        v  (scraping.py / site_config.py / weapons.py)
[HTML Parsing & Data Cleaning]
        |
        v  (indexer.py)
[Local Embeddings via LM Studio]
        |
        v
[In-Memory Vector Store]  --> (Planned: Supabase / pgvector)
        |
        v  (Cosine Similarity + Threshold > 0.6)
[Semantic Retrieval + Local LLM via Ollama] --> [Grounded Answer]
```

### Key Technical Highlights
- **Zero API Costs:** Uses **LM Studio** (via OpenAI-compatible API) for embedding generation and **Ollama** running `Llama-3.2-1B-Instruct` locally for inference.
- **Custom Vector Search & Thresholding:** Implements from-scratch cosine similarity retrieval (`top_n=3`) with a strict similarity threshold (`> 0.6`) to filter out irrelevant wiki pages before generation.
- **Anti-Hallucination Prompting:** Enforces strict grounding rules in the system prompt, answering directly from retrieved excerpts in the user's language, or falling back to `"I don't know."` when data is missing.

---

## Project Structure

```text
├── weapons.py       # URL definitions and metadata for Dark Souls 2 weapons
├── site_config.py   # Restricted site registry (RESTRICTED_SITES) and category mappings
├── scraping.py      # Fextralife web scraping and HTML extraction logic (scrape_fextralife)
├── indexer.py       # In-memory vector indexing, cosine similarity retrieval, and RAG CLI
├── .env.example     # Environment variables configuration
└── .gitignore       # Ignored files and local environment exclusions
```

---

## Setup & Configuration

### 1. Prerequisites
- **Python 3.10+**
- **[LM Studio](https://lmstudio.ai/):** Running locally with an embedding model loaded (e.g., `nomic-embed-text` or `bge-small`).
- **[Ollama](https://ollama.com/):** Running locally with the Hugging Face GGUF model pulled:
  ```bash
  ollama pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF
  ```

### 2. Environment Variables
Create a `.env` file in the root directory based on the template below:

```env
EMBEDDING_BASE_URL=http://localhost:1234/v1
EMBEDDING_API_KEY=lm-studio
EMBEDDING_MODEL=your-local-embedding-model
EMBEDDING_DIM=768

# Upcoming integration
SUPABASE_URL=""
SUPABASE_KEY=""
```

### 3. Running the Pipeline
```bash
# Install dependencies
pip install -r requirements.txt

# Index wiki pages and start the interactive Q&A CLI
python indexer.py
```

---

## Roadmap & Current Status

- [x] **Web Scraping & Cleaning:** Automated extraction of *Dark Souls 2* Fextralife pages (`scraping.py`, `site_config.py`, `weapons.py`).
- [x] **Local Embedding Pipeline:** Vector generation using LM Studio (`indexer.py`).
- [x] **Local RAG Inference:** From-scratch cosine similarity retrieval (`> 0.6` threshold) connected to Ollama (`Llama-3.2-1B-Instruct`) with streaming output.
- [ ] **Text Chunking:** Split long wiki pages into smaller overlapping chunks for finer-grained retrieval.
- [ ] **Vector Database:** Migrate from in-memory vector storage to **Supabase (`pgvector`)** to avoid re-scraping on every run.
