import sys
from pathlib import Path
from src.ingest.parse import parse_pdf
from src.ingest.chunk import chunk_pages
from src.index.embed import embed_passages
from src.index.store import get_client, ensure_collection, upsert_chunks


def main(pdf_path: str) -> None:
    source = Path(pdf_path).stem
    pages = parse_pdf(pdf_path)
    print(f"parsed {len(pages)} pages")
    chunks = chunk_pages(pages, source=source)
    print(f"created {len(chunks)} chunks")
    vectors = embed_passages([c.text for c in chunks])
    print(f"embedded {vectors.shape}")
    client = get_client()
    ensure_collection(client)
    upsert_chunks(client, chunks, vectors)
    print(f"indexed '{source}'")


if __name__ == "__main__":
    main(sys.argv[1])