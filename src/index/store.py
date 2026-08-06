import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

COLLECTION = "filings"
DIM = 384


def get_client() -> QdrantClient:
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
        PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, c.id)),
            vector=vec.tolist(),
            payload={"text": c.text, "page_number": c.page_number, "source": c.source},
        )
        for c, vec in zip(chunks, vectors)
    ]
    client.upsert(collection_name=COLLECTION, points=points)


def search(client, query_vector, limit: int = 20):
    result = client.query_points(collection_name=COLLECTION,
                                  query=query_vector.tolist(), limit=limit)
    return result.points