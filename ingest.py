import json

import chromadb
from chromadb.utils import embedding_functions

RAW_DATA_PATH = "data/raw/pages.json"
CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "web_knowledge"


def chunk_text(text, size=200, overlap=30):
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i : i + size]))
        i += size - overlap
    return chunks


def main():
    with open(RAW_DATA_PATH) as f:
        pages = json.load(f)

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
    )

    documents, metadatas, ids = [], [], []
    for page in pages:
        for idx, chunk in enumerate(chunk_text(page["content"])):
            documents.append(chunk)
            metadatas.append({"source": page["url"], "chunk": idx})
            ids.append(f"{page['url']}#{idx}")

    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)

    print(f"Indexed {len(documents)} chunks from {len(pages)} pages")
    print(f"Collection now holds {collection.count()} chunks")


if __name__ == "__main__":
    main()
