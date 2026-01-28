from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline


logger = logging.getLogger(__name__)


@dataclass
class SectionSummary:
    section_name: str
    summary: str


@dataclass
class FullReportSummary:
    executive_summary: str
    section_summaries: List[SectionSummary]
    commitments: List[str]


class Summariser:
    """
    Summarisation service built on top of HuggingFace transformers.
    """

    def __init__(self, model_name: str = "facebook/bart-large-cnn") -> None:
        self.model_name = model_name
        self._pipeline = None

    def _load_pipeline(self):
        if self._pipeline is not None:
            return self._pipeline

        try:
            device = 0 if torch.cuda.is_available() else -1
        except Exception:  # pragma: no cover - extremely defensive
            device = -1

        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self._pipeline = pipeline(
                "summarization",
                model=model,
                tokenizer=tokenizer,
                device=device,
            )
        except Exception as exc:  # pragma: no cover - model loading issues
            logger.exception("Failed to load summarisation model %s", self.model_name)
            raise RuntimeError(f"Failed to load summarisation model: {exc}") from exc

        return self._pipeline

    def summarise_section(self, text: str, max_length: int = 150) -> str:
        if not text.strip():
            return ""

        pipe = self._load_pipeline()
        # Handle long text by chunking.
        inputs = self._chunk_for_model(text, max_tokens=1024)
        summaries: List[str] = []
        for chunk in inputs:
            result = pipe(chunk, max_length=max_length, min_length=max_length // 3, truncation=True)
            summaries.append(result[0]["summary_text"])
        if len(summaries) == 1:
            return summaries[0].strip()
        # Summarise the summaries for very long sections.
        combined = " ".join(summaries)
        result = pipe(combined, max_length=max_length, min_length=max_length // 3, truncation=True)
        return result[0]["summary_text"].strip()

    def _chunk_for_model(self, text: str, max_tokens: int) -> List[str]:
        # Approximate token limit via characters; transformers will truncate precisely.
        avg_chars_per_token = 4
        max_chars = max_tokens * avg_chars_per_token
        chunks: List[str] = []
        current = ""

        for sentence in text.split(". "):
            sentence = sentence.strip()
            if not sentence:
                continue
            extension = (sentence + ". ").strip()
            if len(current) + len(extension) > max_chars and current:
                chunks.append(current.strip())
                current = extension
            else:
                if current:
                    current += " " + extension
                else:
                    current = extension

        if current:
            chunks.append(current.strip())

        return chunks

    def extract_key_commitments(self, text: str) -> List[str]:
        commitments: List[str] = []
        patterns = [
            r"commit to .*? by \d{4}",
            r"target of .*? by \d{4}",
            r"achieve net[- ]zero by \d{4}",
            r"will reduce .*? by .*?(?:\d{4}|within \d+ years)",
            r"pledge to .*?(?:\d{4})?",
        ]
        import re

        combined_pattern = re.compile("|".join(patterns), re.IGNORECASE)
        for match in combined_pattern.finditer(text):
            snippet = match.group(0).strip()
            if snippet not in commitments:
                commitments.append(snippet)
        return commitments

    def summarise_full_report(self, sections_dict: Dict[str, str]) -> FullReportSummary:
        section_summaries: List[SectionSummary] = []
        all_text_parts: List[str] = []

        for name, text in sections_dict.items():
            summary = self.summarise_section(text)
            section_summaries.append(SectionSummary(section_name=name, summary=summary))
            all_text_parts.append(text)

        combined_text = "\n".join(all_text_parts)
        executive_summary = self.summarise_section(combined_text, max_length=200)
        commitments = self.extract_key_commitments(combined_text)

        return FullReportSummary(
            executive_summary=executive_summary,
            section_summaries=section_summaries,
            commitments=commitments,
        )

