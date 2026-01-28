from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import fitz  # type: ignore[attr-defined]


logger = logging.getLogger(__name__)


@dataclass
class PageText:
    page_number: int
    text: str


@dataclass
class TableData:
    page_number: int
    bbox: tuple
    text: str


@dataclass
class PdfMetadata:
    title: Optional[str]
    author: Optional[str]
    creation_date: Optional[str]
    modification_date: Optional[str]
    additional: Dict[str, Optional[str]]


@dataclass
class SectionText:
    name: str
    pages: List[int]
    text: str


@dataclass
class PdfExtractionResult:
    pages: List[PageText]
    tables: List[TableData]
    metadata: PdfMetadata
    sections: List[SectionText]


class PDFExtractor:
    """
    Service responsible for extracting text, tables, metadata and sections
    from PDF sustainability reports.
    """

    SECTION_KEYWORDS = [
        "environmental performance",
        "carbon emissions",
        "climate strategy",
        "climate-related",
        "ghg emissions",
        "greenhouse gas",
        "water management",
        "water stewardship",
        "energy use",
        "energy management",
        "waste management",
        "scope 1",
        "scope 2",
        "scope 3",
    ]

    def __init__(self, reports_dir: Path) -> None:
        self.reports_dir = reports_dir

    def _clean_text(self, text: str) -> str:
        # Basic cleanup: normalize whitespace and some common OCR artefacts
        cleaned = " ".join(text.replace("\u00ad", "").split())
        cleaned = cleaned.replace("0 ", "0").replace("1 ", "1")
        return cleaned

    def _extract_metadata(self, doc: fitz.Document) -> PdfMetadata:
        meta = doc.metadata or {}
        return PdfMetadata(
            title=meta.get("title"),
            author=meta.get("author"),
            creation_date=meta.get("creationDate"),
            modification_date=meta.get("modDate"),
            additional={k: v for k, v in meta.items() if k not in {"title", "author", "creationDate", "modDate"}},
        )

    def _detect_tables(self, doc: fitz.Document) -> List[TableData]:
        """
        Heuristic table detection based on text blocks with many columns.
        This is intentionally simple and can be improved later.
        """
        tables: List[TableData] = []
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            blocks = page.get_text("blocks")
            for x0, y0, x1, y1, text, *_ in blocks:
                lines = text.splitlines()
                if not lines:
                    continue
                # Very naive heuristic: multiple lines with repeated separators
                has_table_like_structure = sum(1 for line in lines if "\t" in line or "  " in line) >= 3
                if has_table_like_structure:
                    tables.append(
                        TableData(
                            page_number=page_index + 1,
                            bbox=(float(x0), float(y0), float(x1), float(y1)),
                            text=self._clean_text(text),
                        )
                    )
        return tables

    def _detect_sections(self, pages: List[PageText]) -> List[SectionText]:
        """
        Detect and group sections by scanning for headings containing known keywords.
        """
        sections: List[SectionText] = []
        current_section_name = "Document"
        current_pages: List[int] = []
        current_text_parts: List[str] = []

        def flush_current() -> None:
            nonlocal current_section_name, current_pages, current_text_parts
            if current_pages and current_text_parts:
                sections.append(
                    SectionText(
                        name=current_section_name,
                        pages=current_pages.copy(),
                        text="\n".join(current_text_parts),
                    )
                )
            current_pages = []
            current_text_parts = []

        for page in pages:
            text = page.text
            lowered = text.lower()
            # Check if any keyword appears early on the page, treat as a new section
            section_found: Optional[str] = None
            for keyword in self.SECTION_KEYWORDS:
                idx = lowered.find(keyword)
                if 0 <= idx <= 300:  # heading appears near top
                    section_found = keyword.title()
                    break

            if section_found is not None and (current_pages or current_text_parts):
                flush_current()
                current_section_name = section_found

            current_pages.append(page.page_number)
            current_text_parts.append(text)

        # Flush remaining
        flush_current()

        if not sections:
            # Fallback: single generic section
            combined_text = "\n".join(p.text for p in pages)
            sections.append(SectionText(name="Document", pages=[p.page_number for p in pages], text=combined_text))

        return sections

    def extract_all(self, filename: str) -> PdfExtractionResult:
        """
        Extract full document text with page numbers, metadata, tables and section labels.
        """
        pdf_path = self.reports_dir / filename
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        try:
            doc = fitz.open(pdf_path)  # type: ignore[call-arg]
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Failed to open PDF %s", pdf_path)
            raise RuntimeError(f"Failed to open PDF: {exc}") from exc

        try:
            pages: List[PageText] = []
            for page_index in range(doc.page_count):
                page = doc.load_page(page_index)
                text = page.get_text()
                pages.append(PageText(page_number=page_index + 1, text=self._clean_text(text)))

            metadata = self._extract_metadata(doc)
            tables = self._detect_tables(doc)
            sections = self._detect_sections(pages)

            return PdfExtractionResult(
                pages=pages,
                tables=tables,
                metadata=metadata,
                sections=sections,
            )
        finally:
            doc.close()

