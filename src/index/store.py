from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

COLLECTION = "filings"
DIM = 384  # bge-small-en-v1.5 output size


def get_client() -> QdrantClient:
    # EMBEDDED mode for now (no Docker). Switch to url="http://localhost:6333" on Thursday.
    return QdrantClient(path="./qdrant_storage")


def ensure_collection(client) -> None:
    names = [c.name for c in client.get_collections().collections]
    if COLLECTION not in names:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=DIM, distance=Distance.COSINE),
        )


def upsert_chunks(client, chunks, vectors) -> None:
    points = [
        PointStruct(id=i, vector=vec.tolist(),
                    payload={"text": c.text, "page_number": c.page_number, "source": c.source})
        for i, (c, vec) in enumerate(zip(chunks, vectors))
    ]
    client.upsert(collection_name=COLLECTION, points=points)


def search(client, query_vector, limit: int = 20):
    return client.search(collection_name=COLLECTION,
                         query_vector=query_vector.tolist(), limit=limit)