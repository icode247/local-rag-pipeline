import json
import sys

import chromadb
import requests
from chromadb.utils import embedding_functions

CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "web_knowledge"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"

PROMPT_TEMPLATE = """You are a research assistant. Answer the question using only the context below.
If the context does not contain the answer, say you don't have enough information.

Context:
{context}

Question: {question}

Answer:"""


def retrieve(question, n_results=3):
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.get_collection(
        name=COLLECTION_NAME, embedding_function=embed_fn
    )
    results = collection.query(query_texts=[question], n_results=n_results)
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    return chunks, sources


def generate(question, chunks):
    prompt = PROMPT_TEMPLATE.format(context="\n\n".join(chunks), question=question)
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": True},
        timeout=(10, 300),  # 10s connect, 300s read-between-chunks
        stream=True,
    )
    response.raise_for_status()
    parts = []
    for line in response.iter_lines():
        if not line:
            continue
        data = json.loads(line)
        parts.append(data.get("response", ""))
        if data.get("done"):
            break
    return "".join(parts)


def main(question):
    chunks, sources = retrieve(question)
    answer = generate(question, chunks)

    print("\n=== Answer ===")
    print(answer.strip())
    print("\n=== Sources ===")
    for src in dict.fromkeys(sources):  # de-duplicate, keep order
        print(f"  - {src}")


if __name__ == "__main__":
    main(" ".join(sys.argv[1:]))
