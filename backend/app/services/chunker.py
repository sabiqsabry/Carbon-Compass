from __future__ import annotations

from dataclasses import dataclass
from typing import Generator, Iterable, List, Optional

from .pdf_extractor import SectionText


@dataclass
class Chunk:
    text: str
    start_char: int
    end_char: int
    page_numbers: List[int]
    section_name: Optional[str]


class Chunker:
    """
    Splits extracted PDF text into overlapping chunks suitable for NLP models.
    """

    def __init__(self, chunk_size: int = 1000, overlap: int = 200) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def _split_into_sentences(self, text: str) -> List[str]:
        # Simple sentence splitter based on punctuation.
        sentences: List[str] = []
        current = []
        for ch in text:
            current.append(ch)
            if ch in {".", "!", "?"}:
                sentence = "".join(current).strip()
                if sentence:
                    sentences.append(sentence)
                current = []
        if current:
            sentence = "".join(current).strip()
            if sentence:
                sentences.append(sentence)
        return sentences

    def _generate_chunks_for_section(self, section: SectionText) -> Generator[Chunk, None, None]:
        text = section.text
        sentences = self._split_into_sentences(text)
        if not sentences:
            return

        current_text = ""
        current_start = 0

        for sentence in sentences:
            # If adding this sentence would exceed chunk_size, yield current chunk.
            if current_text and len(current_text) + 1 + len(sentence) > self.chunk_size:
                end_char = current_start + len(current_text)
                yield Chunk(
                    text=current_text,
                    start_char=current_start,
                    end_char=end_char,
                    page_numbers=section.pages,
                    section_name=section.name,
                )
                # Start new chunk with overlap from end of previous chunk.
                overlap_text = current_text[-self.overlap :] if self.overlap < len(current_text) else current_text
                current_start = end_char - len(overlap_text)
                current_text = overlap_text

            if current_text:
                current_text += " " + sentence
            else:
                current_text = sentence

        if current_text:
            end_char = current_start + len(current_text)
            yield Chunk(
                text=current_text,
                start_char=current_start,
                end_char=end_char,
                page_numbers=section.pages,
                section_name=section.name,
            )

    def chunk_sections(self, sections: Iterable[SectionText]) -> Generator[Chunk, None, None]:
        """
        Chunk all sections, yielding a generator for memory efficiency.
        """
        for section in sections:
            yield from self._generate_chunks_for_section(section)

