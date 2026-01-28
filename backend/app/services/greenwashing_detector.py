from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List

from .chunker import Chunk


class IndicatorType(str, Enum):
    VAGUE_CLAIM = "VAGUE_CLAIM"
    NO_BASELINE = "NO_BASELINE"
    NO_TIMELINE = "NO_TIMELINE"
    NO_PROOF = "NO_PROOF"
    ASPIRATIONAL_ONLY = "ASPIRATIONAL_ONLY"
    CHERRY_PICKING = "CHERRY_PICKING"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class GreenwashingFlag:
    indicator_type: IndicatorType
    text: str
    explanation: str
    severity: Severity
    confidence: float


@dataclass
class GreenwashingResult:
    flags: List[GreenwashingFlag]
    risk_score: float  # 0-100, higher = more greenwashing risk


class GreenwashingDetector:
    """
    Detects potential greenwashing patterns in sustainability reports using heuristics.
    """

    VAGUE_BUZZWORDS = [
        "committed to sustainability",
        "environmentally conscious",
        "working towards",
        "striving to",
        "planet-positive",
        "eco[- ]?friendly",
        "green future",
        "sustainable future",
    ]

    def __init__(self) -> None:
        self._vague_pattern = re.compile("|".join(self.VAGUE_BUZZWORDS), re.IGNORECASE)
        self._number_pattern = re.compile(r"\d")
        self._timeline_pattern = re.compile(r"\bby\s+20\d{2}\b", re.IGNORECASE)
        self._baseline_pattern = re.compile(r"\bfrom\s+20\d{2}\b|\bversus\s+20\d{2}\b", re.IGNORECASE)
        self._verification_pattern = re.compile(
            r"\b(gr[il]|cdp|tcfd|sbti|iso\s*14001|third[- ]party|independent assurance)\b", re.IGNORECASE
        )

    def _flag_vague_claims(self, text: str) -> List[GreenwashingFlag]:
        flags: List[GreenwashingFlag] = []
        for match in self._vague_pattern.finditer(text):
            snippet = text[max(0, match.start() - 80) : match.end() + 80]
            flags.append(
                GreenwashingFlag(
                    indicator_type=IndicatorType.VAGUE_CLAIM,
                    text=snippet.strip(),
                    explanation="Vague environmental buzzword without accompanying specifics.",
                    severity=Severity.MEDIUM,
                    confidence=0.8,
                )
            )
        return flags

    def _flag_no_timeline_or_baseline(self, text: str) -> List[GreenwashingFlag]:
        flags: List[GreenwashingFlag] = []
        # Look for "reduce emissions" or "net zero" without year/baseline.
        target_like = re.finditer(r"(net[- ]?zero|reduce emissions|carbon neutral|climate positive)", text, re.IGNORECASE)
        for match in target_like:
            snippet = text[max(0, match.start() - 80) : match.end() + 80]
            has_timeline = bool(self._timeline_pattern.search(snippet))
            has_baseline = bool(self._baseline_pattern.search(snippet))

            if not has_timeline:
                flags.append(
                    GreenwashingFlag(
                        indicator_type=IndicatorType.NO_TIMELINE,
                        text=snippet.strip(),
                        explanation="Target or commitment without a clear deadline or year.",
                        severity=Severity.MEDIUM,
                        confidence=0.75,
                    )
                )
            if not has_baseline:
                flags.append(
                    GreenwashingFlag(
                        indicator_type=IndicatorType.NO_BASELINE,
                        text=snippet.strip(),
                        explanation="Reduction target without specifying a baseline year or baseline value.",
                        severity=Severity.MEDIUM,
                        confidence=0.75,
                    )
                )
        return flags

    def _flag_no_proof(self, text: str) -> List[GreenwashingFlag]:
        flags: List[GreenwashingFlag] = []
        # Claims like "we are leaders in sustainability" with no numbers or verification.
        claim_pattern = re.compile(
            r"(leader in sustainability|industry-leading|best[- ]in[- ]class|world[- ]class sustainability)",
            re.IGNORECASE,
        )
        for match in claim_pattern.finditer(text):
            snippet = text[max(0, match.start() - 80) : match.end() + 80]
            has_numbers = bool(self._number_pattern.search(snippet))
            has_verification = bool(self._verification_pattern.search(snippet))
            if not (has_numbers or has_verification):
                flags.append(
                    GreenwashingFlag(
                        indicator_type=IndicatorType.NO_PROOF,
                        text=snippet.strip(),
                        explanation="Bold sustainability claim without supporting data or independent verification.",
                        severity=Severity.HIGH,
                        confidence=0.8,
                    )
                )
        return flags

    def _flag_aspirational_only(self, text: str) -> List[GreenwashingFlag]:
        flags: List[GreenwashingFlag] = []
        aspirational_pattern = re.compile(
            r"\b(we aim to|we hope to|we aspire to|we intend to)\b", re.IGNORECASE
        )
        for match in aspirational_pattern.finditer(text):
            snippet = text[max(0, match.start() - 80) : match.end() + 80]
            flags.append(
                GreenwashingFlag(
                    indicator_type=IndicatorType.ASPIRATIONAL_ONLY,
                    text=snippet.strip(),
                    explanation="Aspirational language that may lack firm, measurable commitments.",
                    severity=Severity.LOW,
                    confidence=0.7,
                )
            )
        return flags

    def _flag_cherry_picking(self, text: str) -> List[GreenwashingFlag]:
        flags: List[GreenwashingFlag] = []
        # Heuristic: highlight mentions of "selected sites" or "pilot projects".
        pattern = re.compile(r"(selected sites|pilot projects?|flagship site)", re.IGNORECASE)
        for match in pattern.finditer(text):
            snippet = text[max(0, match.start() - 80) : match.end() + 80]
            flags.append(
                GreenwashingFlag(
                    indicator_type=IndicatorType.CHERRY_PICKING,
                    text=snippet.strip(),
                    explanation="Potential cherry-picking of favorable examples instead of group-wide data.",
                    severity=Severity.MEDIUM,
                    confidence=0.65,
                )
            )
        return flags

    def _compute_risk_score(self, flags: List[GreenwashingFlag]) -> float:
        if not flags:
            return 0.0
        severity_weight = {Severity.LOW: 1.0, Severity.MEDIUM: 2.0, Severity.HIGH: 3.0}
        total_weight = sum(severity_weight[f.severity] * f.confidence for f in flags)
        # Normalise to a 0-100 scale with a soft cap.
        score = min(100.0, total_weight * 5.0)
        return round(score, 2)

    def analyse(self, full_text: str, chunks: Iterable[Chunk]) -> GreenwashingResult:
        # For now primarily use the full text to catch global patterns.
        flags: List[GreenwashingFlag] = []
        flags.extend(self._flag_vague_claims(full_text))
        flags.extend(self._flag_no_timeline_or_baseline(full_text))
        flags.extend(self._flag_no_proof(full_text))
        flags.extend(self._flag_aspirational_only(full_text))
        flags.extend(self._flag_cherry_picking(full_text))

        risk_score = self._compute_risk_score(flags)
        return GreenwashingResult(flags=flags, risk_score=risk_score)

