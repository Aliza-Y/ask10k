from dataclasses import dataclass
from pathlib import Path
import fitz


@dataclass
class Page:
    page_number: int
    text: str


def parse_pdf(path: str | Path) -> list[Page]:
    """Extract text from a PDF, one Page per physical page.

    Page numbers are 1-indexed to match what a human sees in a viewer.
    """
    doc = fitz.open(path)
    pages: list[Page] = []
    for i, page in enumerate(doc, start=1):
        text = page.get_text("text")
        if text and text.strip():
            pages.append(Page(page_number=i, text=text))
    doc.close()
    return pages