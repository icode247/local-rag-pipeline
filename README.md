# local-rag-pipeline

A minimal, fully local Retrieval-Augmented Generation (RAG) pipeline in three small scripts. It scrapes web pages, embeds them into a local vector store, and answers questions over them using a locally-running LLM.

```
collect.py  ──►  data/raw/pages.json  ──►  ingest.py  ──►  data/chroma  ──►  rag.py  ──►  answer
  (scrape)                                  (chunk +                          (retrieve +
                                            embed)                            generate)
```

## How it works

| Stage | Script | What it does |
|-------|--------|--------------|
| **Collect** | `collect.py` | Fetches a list of target URLs as Markdown via the [Bright Data](https://brightdata.com) Web Unlocker API and saves them to `data/raw/pages.json`. |
| **Ingest** | `ingest.py` | Splits each page into overlapping word chunks, embeds them with the `all-MiniLM-L6-v2` sentence-transformer, and upserts them into a persistent [ChromaDB](https://www.trychroma.com) collection (`web_knowledge`) at `data/chroma`. |
| **Query** | `rag.py` | Embeds your question, retrieves the top-k matching chunks from Chroma, and asks a local [Ollama](https://ollama.com) model (`llama3.2:3b`) to answer using only that context — printing the answer and its sources. |

Everything except the initial scrape runs locally: embeddings and the LLM never leave your machine.

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com) running locally with the `llama3.2:3b` model pulled
- A [Bright Data](https://brightdata.com) account with a Web Unlocker zone (only needed to re-scrape pages)

Python dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install requests chromadb sentence-transformers
```

Pull the LLM and make sure Ollama is serving on `localhost:11434`:

```bash
ollama pull llama3.2:3b
ollama serve   # if not already running
```

## Usage

### 1. Collect source pages (optional)

The repo already ships with scraped data and a built Chroma index, so you can skip straight to querying. To re-scrape or change the sources, edit the `TARGETS` list in `collect.py`, then:

```bash
python collect.py
```

This writes `data/raw/pages.json`. By default it scrapes three Wikipedia articles (RAG, vector databases, and large language models). Set your own Bright Data credentials in `collect.py` before running.

### 2. Build the vector index

```bash
python ingest.py
```

This chunks every page (200 words per chunk, 30-word overlap), embeds them, and persists the collection to `data/chroma`. Re-run it any time `pages.json` changes; `upsert` keeps chunk IDs stable so re-ingesting is idempotent.

### 3. Ask questions

```bash
python rag.py "What is retrieval-augmented generation?"
```

Example output:

```
=== Answer ===
Retrieval-augmented generation (RAG) is a technique that ...

=== Sources ===
  - https://en.wikipedia.org/wiki/Retrieval-augmented_generation
```

## Configuration

Key settings live as constants at the top of each script:

| Setting | Location | Default |
|---------|----------|---------|
| Target URLs | `collect.py` → `TARGETS` | 3 Wikipedia pages |
| Chunk size / overlap | `ingest.py` → `chunk_text()` | 200 words / 30 overlap |
| Embedding model | `ingest.py`, `rag.py` | `all-MiniLM-L6-v2` |
| Collection name | `ingest.py`, `rag.py` | `web_knowledge` |
| LLM model | `rag.py` → `MODEL` | `llama3.2:3b` |
| Retrieved chunks (`k`) | `rag.py` → `retrieve()` | 3 |
| Ollama endpoint | `rag.py` → `OLLAMA_URL` | `http://localhost:11434` |

## Project layout

```
.
├── collect.py        # Scrape target URLs → data/raw/pages.json
├── ingest.py         # Chunk + embed → data/chroma (ChromaDB)
├── rag.py            # Retrieve + generate answer via Ollama
└── data/
    ├── raw/          # Scraped page content (JSON)
    └── chroma/       # Persistent vector store
```
