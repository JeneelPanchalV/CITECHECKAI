from dataclasses import dataclass
from typing import List
from pypdf import PdfReader

@dataclass
class PageText:
    page: int
    text: str

def load_pdf_pages(pdf_path: str) -> List[PageText]:
    reader = PdfReader(pdf_path)
    pages = []

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = " ".join(text.split())  # normalize whitespace

        if text.strip():
            pages.append(PageText(page=i, text=text))

    return pages
