from dataclasses import dataclass
import re

from src.ingest.parse import Page


@dataclass
class Chunk:
    id: str
    text: str
    page_number: int
    source: str


def clean(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_pages(
    pages: list[Page],
    source: str,
    target_words: int = 350,
    overlap_words: int = 60,
) -> list[Chunk]:
    """Chunk within page boundaries so every chunk has an exact page citation.

    Tradeoff: a passage spanning a page break gets split. We accept this
    because citation accuracy is the product's core value.
    """
    chunks: list[Chunk] = []
    for page in pages:
        words = clean(page.text).split()
        if not words:
            continue
        start = 0
        while start < len(words):
            end = min(start + target_words, len(words))
            text = " ".join(words[start:end])
            if len(text) > 50:
                chunks.append(
                    Chunk(
                        id=f"{source}-p{page.page_number}-{start}",
                        text=text,
                        page_number=page.page_number,
                        source=source,
                    )
                )
            if end == len(words):
                break
            start = end - overlap_words
    return chunks