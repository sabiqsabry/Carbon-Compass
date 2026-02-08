from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


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

    Uses AutoModelForSeq2SeqLM directly (instead of the pipeline abstraction)
    for compatibility with both transformers v4.x and v5.x.
    """

    def __init__(self, model_name: str = "sshleifer/distilbart-cnn-12-6") -> None:
        self.model_name = model_name
        self._model: AutoModelForSeq2SeqLM | None = None
        self._tokenizer: AutoTokenizer | None = None
        self._device: torch.device | None = None

    def _load_model(self) -> Tuple[AutoTokenizer, AutoModelForSeq2SeqLM]:
        """Load the model and tokenizer, caching for subsequent calls."""
        if self._model is not None and self._tokenizer is not None:
            return self._tokenizer, self._model

        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        except Exception:  # pragma: no cover
            device = torch.device("cpu")

        try:
            logger.info("Loading summarisation model %s ...", self.model_name)
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name).to(device)
            model.eval()

            self._tokenizer = tokenizer
            self._model = model
            self._device = device
            logger.info("Summarisation model loaded successfully on %s", device)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to load summarisation model %s", self.model_name)
            raise RuntimeError(f"Failed to load summarisation model: {exc}") from exc

        return self._tokenizer, self._model

    def summarise_section(self, text: str, max_length: int = 150) -> str:
        """Summarise a section of text using the seq2seq model directly."""
        if not text.strip():
            return ""

        tokenizer, model = self._load_model()
        device = self._device or torch.device("cpu")

        chunks = self._chunk_for_model(text, max_tokens=1024)
        summaries: List[str] = []

        for chunk in chunks:
            inputs = tokenizer(
                chunk,
                return_tensors="pt",
                truncation=True,
                max_length=1024,
            ).to(device)

            with torch.no_grad():
                summary_ids = model.generate(
                    **inputs,
                    max_length=max_length,
                    min_length=max(max_length // 4, 8),
                    num_beams=2,
                    length_penalty=1.0,
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                )

            decoded = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            summaries.append(decoded)

        if len(summaries) == 1:
            return summaries[0].strip()

        # Summarise the summaries for very long sections.
        combined = " ".join(summaries)
        inputs = tokenizer(
            combined,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
        ).to(device)

        with torch.no_grad():
            summary_ids = model.generate(
                **inputs,
                max_length=max_length,
                min_length=max(max_length // 4, 8),
                num_beams=2,
                length_penalty=1.0,
                early_stopping=True,
                no_repeat_ngram_size=3,
            )

        return tokenizer.decode(summary_ids[0], skip_special_tokens=True).strip()

    def _chunk_for_model(self, text: str, max_tokens: int) -> List[str]:
        """Split text into chunks that fit within the model's token limit."""
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
        """Extract environmental commitments from text using regex patterns."""
        commitments: List[str] = []
        patterns = [
            # Target / commitment with year
            r"commit(?:ted|s|ment)?\s+to\s+.{10,120}?(?:by\s+\d{4}|\d{4})",
            r"target\s+(?:of|to|is)\s+.{10,120}?(?:by\s+\d{4}|\d{4})",
            r"achieve\s+net[- ]zero\s+.{0,80}?(?:by\s+)?\d{4}",
            r"will\s+reduce\s+.{10,120}?(?:\d{4}|within\s+\d+\s+years)",
            r"pledge[ds]?\s+to\s+.{10,120}?\d{4}",
            # Percentage reduction targets
            r"reduce\s+.{5,80}?(?:emissions?|carbon|co2|ghg).{0,60}?by\s+\d+\s*%",
            r"\d+\s*%\s+reduction\s+in\s+.{5,80}?(?:emissions?|carbon|co2|ghg)",
            # Net-zero / carbon-neutral mentions
            r"(?:carbon[- ]?neutral|net[- ]?zero)\s+.{0,80}?(?:by\s+)?\d{4}",
            # Renewable energy targets
            r"\d+\s*%\s+renewable\s+energy\s+.{0,60}?(?:by\s+)?\d{4}",
            # "aim to" / "plan to" with quantitative targets
            r"(?:aim|plan|seek|intend)s?\s+to\s+.{10,120}?(?:\d+\s*%|\d{4})",
        ]

        combined_pattern = re.compile("|".join(patterns), re.IGNORECASE)
        for match in combined_pattern.finditer(text):
            snippet = match.group(0).strip()
            # Skip very short or duplicate matches
            if len(snippet) < 15:
                continue
            if snippet not in commitments:
                commitments.append(snippet)

        return commitments

    def summarise_full_report(self, sections_dict: Dict[str, str]) -> FullReportSummary:
        """Summarise all sections of a report and extract commitments."""
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
