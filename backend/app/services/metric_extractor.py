from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .chunker import Chunk


class MetricType(str, Enum):
    CARBON_EMISSIONS = "carbon_emissions"
    ENERGY = "energy"
    WATER = "water"
    WASTE = "waste"
    RENEWABLE_PERCENTAGE = "renewable_percentage"
    REDUCTION_TARGET = "reduction_target"


@dataclass
class Metric:
    metric_type: MetricType
    value: float
    unit: str
    year: Optional[int]
    scope: Optional[str]
    context: str
    confidence: float


@dataclass
class MetricExtractionResult:
    metrics: List[Metric]


class MetricExtractor:
    """
    Extracts environmental metrics from chunks of sustainability reports using
    regex-based pattern matching.
    """

    # Regex patterns for different metric types.
    _NUMBER = r"(?P<number>\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?)"
    _YEAR = r"(?P<year>20\d{2}|19\d{2})"

    CARBON_PATTERN = re.compile(
        rf"(?P<scope>scope\s*[123]|total)?[^\d%]{{0,20}}{_NUMBER}\s*(?P<unit>tco2e|tonnes? ?co2e?|mtco2e|ktco2e|mt|kt)",
        re.IGNORECASE,
    )

    ENERGY_PATTERN = re.compile(
        rf"{_NUMBER}\s*(?P<unit>kwh|mwh|gwh|twh|gj|tj)",
        re.IGNORECASE,
    )

    WATER_PATTERN = re.compile(
        rf"{_NUMBER}\s*(?P<unit>m3|cubic meters?|litres?|liters?|gallons?|ml)",
        re.IGNORECASE,
    )

    WASTE_PATTERN = re.compile(
        rf"{_NUMBER}\s*(?P<unit>tonnes?|tons?|kg|kilograms?)",
        re.IGNORECASE,
    )

    RENEWABLE_PATTERN = re.compile(
        rf"{_NUMBER}\s*%[^.]*\brenewable\b",
        re.IGNORECASE,
    )

    REDUCTION_TARGET_PATTERN = re.compile(
        rf"reduc\w*[^\d%]{{0,20}}{_NUMBER}\s*%[^\d]{{0,40}}(?:by|before|in)\s+{_YEAR}",
        re.IGNORECASE,
    )

    MULTIPLIER_PATTERN = re.compile(r"\b(million|billion|thousand|k)\b", re.IGNORECASE)

    def _apply_multiplier(self, value: float, context: str) -> float:
        match = self.MULTIPLIER_PATTERN.search(context)
        if not match:
            return value
        word = match.group(1).lower()
        if word in {"million"}:
            return value * 1_000_000
        if word in {"billion"}:
            return value * 1_000_000_000
        if word in {"thousand", "k"}:
            return value * 1_000
        return value

    def _parse_number(self, raw: str, context: str) -> Optional[float]:
        cleaned = raw.replace(",", "").replace(" ", "")
        try:
            value = float(cleaned)
        except ValueError:
            return None
        return self._apply_multiplier(value, context)

    def _extract_year(self, text: str) -> Optional[int]:
        match = re.search(self._YEAR, text)
        if match:
            try:
                return int(match.group("year"))
            except ValueError:
                return None
        return None

    def _make_metric(
        self,
        metric_type: MetricType,
        match: re.Match[str],
        chunk: Chunk,
        extra_ctx: Optional[str] = None,
        scope_group: str = "scope",
    ) -> Optional[Metric]:
        groups = match.groupdict()
        number_raw = groups.get("number") or match.group(0)
        context_text = extra_ctx or chunk.text
        value = self._parse_number(number_raw, context_text)
        if value is None:
            return None

        unit = (groups.get("unit") or "").strip()
        year = self._extract_year(context_text)
        scope = groups.get(scope_group)
        if scope:
            scope = scope.strip().title()

        confidence = 0.8  # heuristic baseline; could be refined
        return Metric(
            metric_type=metric_type,
            value=value,
            unit=unit,
            year=year,
            scope=scope,
            context=context_text.strip(),
            confidence=confidence,
        )

    def _deduplicate(self, metrics: Sequence[Metric]) -> List[Metric]:
        seen: Dict[Tuple[MetricType, float, str, Optional[int], Optional[str]], Metric] = {}
        for m in metrics:
            key = (m.metric_type, m.value, m.unit, m.year, m.scope)
            if key not in seen:
                seen[key] = m
        return list(seen.values())

    def extract_from_chunks(self, chunks: Iterable[Chunk]) -> MetricExtractionResult:
        metrics: List[Metric] = []

        for chunk in chunks:
            text = chunk.text

            for match in self.CARBON_PATTERN.finditer(text):
                metric = self._make_metric(MetricType.CARBON_EMISSIONS, match, chunk)
                if metric:
                    metrics.append(metric)

            for match in self.ENERGY_PATTERN.finditer(text):
                metric = self._make_metric(MetricType.ENERGY, match, chunk)
                if metric:
                    metrics.append(metric)

            for match in self.WATER_PATTERN.finditer(text):
                metric = self._make_metric(MetricType.WATER, match, chunk)
                if metric:
                    metrics.append(metric)

            for match in self.WASTE_PATTERN.finditer(text):
                metric = self._make_metric(MetricType.WASTE, match, chunk)
                if metric:
                    metrics.append(metric)

            for match in self.RENEWABLE_PATTERN.finditer(text):
                metric = self._make_metric(MetricType.RENEWABLE_PERCENTAGE, match, chunk, extra_ctx=match.group(0))
                if metric:
                    metrics.append(metric)

            for match in self.REDUCTION_TARGET_PATTERN.finditer(text):
                metric = self._make_metric(MetricType.REDUCTION_TARGET, match, chunk, extra_ctx=match.group(0))
                if metric:
                    metrics.append(metric)

        deduped = self._deduplicate(metrics)
        return MetricExtractionResult(metrics=deduped)

