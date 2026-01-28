from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .chunker import Chunker
from .greenwashing_detector import GreenwashingDetector, GreenwashingResult
from .metric_extractor import MetricExtractionResult, MetricExtractor
from .pdf_extractor import PDFExtractor, PdfExtractionResult
from .risk_scorer import RiskScore, RiskScorer
from .summariser import FullReportSummary, Summariser


logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    pdf: PdfExtractionResult
    chunks_count: int
    metrics: MetricExtractionResult
    greenwashing: GreenwashingResult
    summary: FullReportSummary
    risk: RiskScore
    timings: Dict[str, float]


class AnalysisOrchestrator:
    """
    Ties together all NLP services into a single analysis pipeline.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        reports_dir = project_root / "reports"
        self.pdf_extractor = PDFExtractor(reports_dir=reports_dir)
        self.chunker = Chunker()
        self.metric_extractor = MetricExtractor()
        self.greenwashing_detector = GreenwashingDetector()
        self.summariser = Summariser()
        self.risk_scorer = RiskScorer()
        self._cache: Dict[str, AnalysisResult] = {}

    def _report_progress(self, step: str, current: int, total: int) -> None:
        percent = int((current / total) * 100)
        logger.info("Analysis progress: %s (%d/%d, %d%%)", step, current, total, percent)

    def analyse(self, filename: str, use_cache: bool = True) -> AnalysisResult:
        if use_cache and filename in self._cache:
            return self._cache[filename]

        timings: Dict[str, float] = {}
        step_count = 6
        current_step = 0

        # Step a: PDF extraction
        start = time.perf_counter()
        pdf_result = self.pdf_extractor.extract_all(filename)
        timings["pdf_extraction"] = time.perf_counter() - start
        current_step += 1
        self._report_progress("PDF extraction", current_step, step_count)

        # Step b: Text chunking
        start = time.perf_counter()
        chunks = list(self.chunker.chunk_sections(pdf_result.sections))
        timings["chunking"] = time.perf_counter() - start
        current_step += 1
        self._report_progress("Text chunking", current_step, step_count)

        # Step c: Metric extraction
        start = time.perf_counter()
        metrics_result = self.metric_extractor.extract_from_chunks(chunks)
        timings["metric_extraction"] = time.perf_counter() - start
        current_step += 1
        self._report_progress("Metric extraction", current_step, step_count)

        # Prepare full text for greenwashing and summarisation.
        full_text = "\n".join(page.text for page in pdf_result.pages)

        # Step d: Greenwashing detection
        start = time.perf_counter()
        greenwashing_result: Optional[GreenwashingResult]
        try:
            greenwashing_result = self.greenwashing_detector.analyse(full_text, chunks)
        except Exception:  # pragma: no cover - defensive
            logger.exception("Greenwashing detection failed; continuing with partial results")
            greenwashing_result = GreenwashingResult(flags=[], risk_score=0.0)
        timings["greenwashing_detection"] = time.perf_counter() - start
        current_step += 1
        self._report_progress("Greenwashing detection", current_step, step_count)

        # Step e: Summarisation
        start = time.perf_counter()
        sections_dict = {s.name: s.text for s in pdf_result.sections}
        try:
            summary_result = self.summariser.summarise_full_report(sections_dict)
        except Exception:  # pragma: no cover - summarisation may be disabled
            logger.exception("Summarisation failed; continuing with partial results")
            summary_result = FullReportSummary(executive_summary="", section_summaries=[], commitments=[])
        timings["summarisation"] = time.perf_counter() - start
        current_step += 1
        self._report_progress("Summarisation", current_step, step_count)

        # Step f: Risk scoring
        start = time.perf_counter()
        risk_result = self.risk_scorer.score(full_text, metrics_result, greenwashing_result)
        timings["risk_scoring"] = time.perf_counter() - start
        current_step += 1
        self._report_progress("Risk scoring", current_step, step_count)

        result = AnalysisResult(
            pdf=pdf_result,
            chunks_count=len(chunks),
            metrics=metrics_result,
            greenwashing=greenwashing_result,
            summary=summary_result,
            risk=risk_result,
            timings=timings,
        )
        self._cache[filename] = result
        return result

