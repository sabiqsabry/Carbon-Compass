from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

from .greenwashing_detector import GreenwashingResult
from .metric_extractor import MetricExtractionResult, MetricType


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskComponentScores:
    transparency: float
    commitment: float
    credibility: float
    data_quality: float
    verification: float


@dataclass
class RiskScore:
    overall_score: float  # 0-100, higher = more risk
    risk_level: RiskLevel
    components: RiskComponentScores
    recommendations: List[str]


class RiskScorer:
    """
    Calculates environmental risk scores based on metrics and greenwashing analysis.
    """

    def _score_transparency(self, metrics: MetricExtractionResult) -> float:
        # Simple proxy: more distinct metric types disclosed => higher transparency.
        disclosed_types = {m.metric_type for m in metrics.metrics}
        max_types = len(MetricType)
        if max_types == 0:
            return 0.0
        score = (len(disclosed_types) / max_types) * 100.0
        return max(0.0, min(100.0, score))

    def _score_commitment(self, full_text: str) -> float:
        from .summariser import Summariser

        # Use commitment extraction as a proxy; more commitments with years => higher score.
        summariser = Summariser()
        commitments = summariser.extract_key_commitments(full_text)
        if not commitments:
            return 20.0
        count = len(commitments)
        score = min(100.0, 40.0 + count * 10.0)
        return score

    def _score_credibility(self, greenwashing: GreenwashingResult) -> float:
        # Inverse of greenwashing risk.
        return max(0.0, 100.0 - greenwashing.risk_score)

    def _score_data_quality(self, metrics: MetricExtractionResult) -> float:
        # Heuristic: presence of years and scopes improves data quality.
        if not metrics.metrics:
            return 20.0
        with_year = sum(1 for m in metrics.metrics if m.year is not None)
        with_scope = sum(1 for m in metrics.metrics if m.scope)
        ratio = (with_year + with_scope) / (2 * len(metrics.metrics))
        return max(0.0, min(100.0, 40.0 + ratio * 60.0))

    def _score_verification(self, full_text: str) -> float:
        import re

        pattern = re.compile(
            r"\b(gr[il]|cdp|tcfd|sbti|iso\s*14001|assurance|independent auditor|limited assurance)\b",
            re.IGNORECASE,
        )
        matches = list(pattern.finditer(full_text))
        if not matches:
            return 20.0
        count = len(matches)
        score = min(100.0, 50.0 + count * 10.0)
        return score

    def _overall_risk(self, components: RiskComponentScores) -> float:
        # Weights from the spec (higher component scores = better, but we invert).
        weights = {
            "transparency": 0.25,
            "commitment": 0.20,
            "credibility": 0.25,
            "data_quality": 0.15,
            "verification": 0.15,
        }
        weighted_average = (
            components.transparency * weights["transparency"]
            + components.commitment * weights["commitment"]
            + components.credibility * weights["credibility"]
            + components.data_quality * weights["data_quality"]
            + components.verification * weights["verification"]
        )
        # Invert so lower component scores => higher risk.
        risk = 100.0 - weighted_average
        return max(0.0, min(100.0, risk))

    def _risk_level(self, overall: float) -> RiskLevel:
        if overall <= 25:
            return RiskLevel.LOW
        if overall <= 50:
            return RiskLevel.MEDIUM
        if overall <= 75:
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL

    def _recommendations(self, components: RiskComponentScores, level: RiskLevel) -> List[str]:
        recs: List[str] = []
        if components.transparency < 60:
            recs.append("Disclose a broader set of environmental metrics with clear units and scopes.")
        if components.commitment < 60:
            recs.append("Strengthen environmental targets with specific percentages and deadlines.")
        if components.credibility < 60:
            recs.append("Reduce vague sustainability language and align claims with quantified data.")
        if components.data_quality < 60:
            recs.append("Improve methodological transparency and ensure metrics include years and scopes.")
        if components.verification < 60:
            recs.append("Seek third-party verification or align reporting with frameworks like GRI, CDP, or SBTi.")
        if not recs and level == RiskLevel.LOW:
            recs.append("Maintain current transparency and continue enhancing long-term climate strategy.")
        return recs

    def score(
        self,
        full_text: str,
        metrics: MetricExtractionResult,
        greenwashing: GreenwashingResult,
    ) -> RiskScore:
        components = RiskComponentScores(
            transparency=self._score_transparency(metrics),
            commitment=self._score_commitment(full_text),
            credibility=self._score_credibility(greenwashing),
            data_quality=self._score_data_quality(metrics),
            verification=self._score_verification(full_text),
        )
        overall = self._overall_risk(components)
        level = self._risk_level(overall)
        recs = self._recommendations(components, level)
        return RiskScore(
            overall_score=round(overall, 2),
            risk_level=level,
            components=components,
            recommendations=recs,
        )

