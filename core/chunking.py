from dataclasses import dataclass
from typing import List
import re

@dataclass
class Chunk:
    chunk_id: str
    page: int
    text: str

def chunk_pages(pages, chunk_size: int = 800, overlap: int = 120) -> List[Chunk]:
    chunks: List[Chunk] = []

    for p in pages:
        words = re.split(r"\s+", p.text)
        start = 0
        idx = 0

        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words).strip()

            if chunk_text:
                chunk_id = f"{p.page}_{idx}_{abs(hash(p.text)) % 10_000}"
                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        page=p.page,
                        text=chunk_text
                    )
                )
                idx += 1

            start = end - overlap
            if start < 0:
                start = 0
            if end == len(words):
                break

    return chunks
