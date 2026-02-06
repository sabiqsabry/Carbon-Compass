"""Verification engine for Carbon Compass.

Compares NLP-extracted metrics from sustainability reports against
calculated emissions from activity data to detect discrepancies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExtractedMetricData:
    """Simplified metric data from NLP extraction for comparison."""
    metric_type: str
    value: float
    unit: str
    scope: Optional[str] = None
    confidence: float = 0.0


@dataclass
class Discrepancy:
    """A discrepancy between reported and calculated values."""
    metric_type: str
    reported_value: float
    reported_unit: str
    calculated_value: float
    calculated_unit: str
    difference_absolute: float
    difference_percentage: float
    severity: str  # minor, moderate, major
    possible_explanations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_type": self.metric_type,
            "reported_value": round(self.reported_value, 2),
            "reported_unit": self.reported_unit,
            "calculated_value": round(self.calculated_value, 2),
            "calculated_unit": self.calculated_unit,
            "difference_absolute": round(self.difference_absolute, 2),
            "difference_percentage": round(self.difference_percentage, 1),
            "severity": self.severity,
            "possible_explanations": self.possible_explanations,
        }


@dataclass
class VerifiedMetric:
    """A metric that has been verified against calculations."""
    metric_type: str
    reported_value: float
    calculated_value: Optional[float]
    status: str  # verified, discrepancy, unverified, not_calculated
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_type": self.metric_type,
            "reported_value": round(self.reported_value, 2),
            "calculated_value": round(self.calculated_value, 2) if self.calculated_value is not None else None,
            "status": self.status,
            "confidence": round(self.confidence, 2),
        }


@dataclass
class VerificationResult:
    """Complete result of a verification comparison."""
    match_score: float  # 0-100
    discrepancies: List[Discrepancy]
    verified_metrics: List[VerifiedMetric]
    summary: str
    recommendations: List[str]
    data_completeness: float  # 0-100, how much data was available for comparison

    def to_dict(self) -> Dict[str, Any]:
        return {
            "match_score": round(self.match_score, 1),
            "discrepancies": [d.to_dict() for d in self.discrepancies],
            "verified_metrics": [m.to_dict() for m in self.verified_metrics],
            "summary": self.summary,
            "recommendations": self.recommendations,
            "data_completeness": round(self.data_completeness, 1),
        }


# Tolerance thresholds for discrepancy severity
MINOR_THRESHOLD = 0.10   # <10%
MODERATE_THRESHOLD = 0.25  # 10-25%
# >25% = major

# Possible explanations for discrepancies
EXPLANATIONS = {
    "underreported": [
        "Different reporting boundaries may exclude some emission sources",
        "Location-based vs market-based methodology differences",
        "Potential understatement of emissions in the report",
        "Some emission sources may have been excluded from reporting",
    ],
    "overreported": [
        "Company may be using conservative estimation methods",
        "Market-based accounting may include additional offsets",
        "Reporting boundaries may be broader than calculation scope",
        "Activity data may not capture all emission sources",
    ],
    "general": [
        "Different reporting periods between report and activity data",
        "Unit conversion differences in methodology",
        "Estimation vs actual measurement differences",
        "Changes in emission factors between reporting years",
    ],
    "scope_mismatch": [
        "Missing Scope 3 categories in the calculation",
        "Supply chain emissions not captured in activity data",
        "Different scope boundary definitions",
    ],
}


class VerificationEngine:
    """Compares NLP-extracted metrics against calculated emissions.

    Identifies discrepancies between what companies report and
    what the activity data suggests.
    """

    def compare(
        self,
        nlp_metrics: List[ExtractedMetricData],
        calculated_by_scope: Dict[str, float],
        calculated_total_kg: float,
        calculated_by_category: Optional[Dict[str, float]] = None,
    ) -> VerificationResult:
        """Compare NLP-extracted metrics against calculated emissions.

        Args:
            nlp_metrics: Metrics extracted from the sustainability report.
            calculated_by_scope: Dict with scope_1, scope_2, scope_3 totals in kg CO2e.
            calculated_total_kg: Total calculated emissions in kg CO2e.
            calculated_by_category: Optional category breakdown in kg CO2e.

        Returns:
            VerificationResult with match score, discrepancies, and recommendations.
        """
        discrepancies: List[Discrepancy] = []
        verified: List[VerifiedMetric] = []
        comparisons_made = 0
        comparisons_possible = 0

        # Convert calculated to tonnes for comparison (reports typically use tonnes)
        calc_total_tonnes = calculated_total_kg / 1000
        calc_scope = {k: v / 1000 for k, v in calculated_by_scope.items()}

        # Find carbon emission metrics from NLP
        emission_metrics = [m for m in nlp_metrics if m.metric_type == "carbon_emissions"]

        for metric in emission_metrics:
            comparisons_possible += 1
            reported = self._normalise_to_tonnes(metric.value, metric.unit)
            if reported is None:
                verified.append(VerifiedMetric(
                    metric_type=self._scope_label(metric.scope),
                    reported_value=metric.value,
                    calculated_value=None,
                    status="unverified",
                    confidence=metric.confidence,
                ))
                continue

            # Match to the right calculated value
            calculated = self._match_to_calculated(metric.scope, calc_scope, calc_total_tonnes)
            if calculated is None:
                verified.append(VerifiedMetric(
                    metric_type=self._scope_label(metric.scope),
                    reported_value=reported,
                    calculated_value=None,
                    status="not_calculated",
                    confidence=metric.confidence,
                ))
                continue

            comparisons_made += 1

            # Calculate discrepancy
            diff_abs = calculated - reported
            diff_pct = abs(diff_abs / reported) * 100 if reported != 0 else 0
            severity = self._classify_severity(diff_pct / 100)

            if severity != "match":
                direction = "underreported" if calculated > reported else "overreported"
                explanations = (
                    EXPLANATIONS[direction][:2]
                    + EXPLANATIONS["general"][:1]
                    + (EXPLANATIONS["scope_mismatch"][:1] if "3" in str(metric.scope) else [])
                )

                discrepancies.append(Discrepancy(
                    metric_type=self._scope_label(metric.scope),
                    reported_value=reported,
                    reported_unit="tonnes CO2e",
                    calculated_value=calculated,
                    calculated_unit="tonnes CO2e",
                    difference_absolute=diff_abs,
                    difference_percentage=diff_pct,
                    severity=severity,
                    possible_explanations=explanations,
                ))

                verified.append(VerifiedMetric(
                    metric_type=self._scope_label(metric.scope),
                    reported_value=reported,
                    calculated_value=calculated,
                    status="discrepancy",
                    confidence=metric.confidence * (1 - diff_pct / 200),
                ))
            else:
                verified.append(VerifiedMetric(
                    metric_type=self._scope_label(metric.scope),
                    reported_value=reported,
                    calculated_value=calculated,
                    status="verified",
                    confidence=metric.confidence,
                ))

        # Calculate overall scores
        match_score = self._calculate_match_score(verified, discrepancies)
        data_completeness = (comparisons_made / max(comparisons_possible, 1)) * 100
        summary = self._generate_summary(match_score, discrepancies, verified)
        recommendations = self._generate_recommendations(discrepancies, verified, calc_scope)

        # Sort discrepancies by severity
        severity_order = {"major": 0, "moderate": 1, "minor": 2}
        discrepancies.sort(key=lambda d: severity_order.get(d.severity, 3))

        return VerificationResult(
            match_score=match_score,
            discrepancies=discrepancies,
            verified_metrics=verified,
            summary=summary,
            recommendations=recommendations,
            data_completeness=data_completeness,
        )

    # ── Private helpers ──────────────────────────────────────────

    @staticmethod
    def _normalise_to_tonnes(value: float, unit: str) -> Optional[float]:
        """Convert a value to tonnes CO2e."""
        unit_lower = unit.lower().strip()
        if "tonne" in unit_lower or "t co2" in unit_lower or unit_lower == "tco2e":
            return value
        if "kg" in unit_lower:
            return value / 1000
        if "mt" in unit_lower or "million" in unit_lower:
            return value * 1_000_000
        if "kt" in unit_lower or "kilo" in unit_lower:
            return value * 1000
        # Assume tonnes if no clear unit
        return value

    @staticmethod
    def _match_to_calculated(
        scope: Optional[str],
        calc_scope: Dict[str, float],
        calc_total: float,
    ) -> Optional[float]:
        """Match a reported metric's scope to the right calculated value."""
        if scope is None:
            return calc_total

        scope_lower = str(scope).lower()
        if "1" in scope_lower:
            val = calc_scope.get("scope_1", 0)
            return val if val > 0 else None
        if "2" in scope_lower:
            val = calc_scope.get("scope_2", 0)
            return val if val > 0 else None
        if "3" in scope_lower:
            val = calc_scope.get("scope_3", 0)
            return val if val > 0 else None
        if "total" in scope_lower or scope_lower == "":
            return calc_total

        return calc_total

    @staticmethod
    def _classify_severity(pct_diff: float) -> str:
        """Classify discrepancy severity based on percentage difference."""
        if pct_diff < MINOR_THRESHOLD:
            return "match"
        if pct_diff < MODERATE_THRESHOLD:
            return "minor"
        if pct_diff < 0.50:
            return "moderate"
        return "major"

    @staticmethod
    def _scope_label(scope: Optional[str]) -> str:
        """Get a human-readable label for a scope."""
        if scope is None:
            return "Total Emissions"
        scope_str = str(scope).lower()
        if "1" in scope_str:
            return "Scope 1 Emissions"
        if "2" in scope_str:
            return "Scope 2 Emissions"
        if "3" in scope_str:
            return "Scope 3 Emissions"
        return "Total Emissions"

    @staticmethod
    def _calculate_match_score(
        verified: List[VerifiedMetric],
        discrepancies: List[Discrepancy],
    ) -> float:
        """Calculate an overall match score (0-100)."""
        if not verified:
            return 0.0

        total = len(verified)
        matched = sum(1 for v in verified if v.status == "verified")
        minor = sum(1 for d in discrepancies if d.severity == "minor")
        moderate = sum(1 for d in discrepancies if d.severity == "moderate")
        major = sum(1 for d in discrepancies if d.severity == "major")

        # Weighted score: matched=100, minor=70, moderate=40, major=10
        score = (matched * 100 + minor * 70 + moderate * 40 + major * 10) / total
        return min(max(score, 0), 100)

    @staticmethod
    def _generate_summary(
        match_score: float,
        discrepancies: List[Discrepancy],
        verified: List[VerifiedMetric],
    ) -> str:
        """Generate a human-readable summary."""
        if not verified:
            return "No comparable metrics found between the report and calculated data."

        major = sum(1 for d in discrepancies if d.severity == "major")
        moderate = sum(1 for d in discrepancies if d.severity == "moderate")
        verified_count = sum(1 for v in verified if v.status == "verified")

        if match_score >= 80:
            base = "Reported figures closely align with calculated estimates."
        elif match_score >= 50:
            base = "Some discrepancies detected between reported and calculated values."
        else:
            base = "Significant discrepancies detected — detailed review recommended."

        details = []
        if verified_count:
            details.append(f"{verified_count} metric(s) verified")
        if major:
            details.append(f"{major} major discrepancy(ies)")
        if moderate:
            details.append(f"{moderate} moderate discrepancy(ies)")

        return f"{base} {', '.join(details)}." if details else base

    @staticmethod
    def _generate_recommendations(
        discrepancies: List[Discrepancy],
        verified: List[VerifiedMetric],
        calc_scope: Dict[str, float],
    ) -> List[str]:
        """Generate actionable recommendations."""
        recs: List[str] = []

        for d in discrepancies:
            if d.severity == "major":
                if d.calculated_value > d.reported_value:
                    recs.append(
                        f"Reported {d.metric_type} ({d.reported_value:,.0f} tonnes) is "
                        f"{d.difference_percentage:.0f}% lower than calculated "
                        f"({d.calculated_value:,.0f} tonnes) — investigate potential understatement"
                    )
                else:
                    recs.append(
                        f"Calculated {d.metric_type} ({d.calculated_value:,.0f} tonnes) is "
                        f"{d.difference_percentage:.0f}% lower than reported "
                        f"({d.reported_value:,.0f} tonnes) — activity data may be incomplete"
                    )

        # Check if scopes are missing
        if calc_scope.get("scope_3", 0) == 0:
            recs.append("Add Scope 3 (supply chain, business travel) activity data for a complete comparison")
        if calc_scope.get("scope_1", 0) == 0:
            recs.append("Add Scope 1 (direct fuel combustion, company vehicles) activity data")

        not_calculated = sum(1 for v in verified if v.status == "not_calculated")
        if not_calculated:
            recs.append(f"{not_calculated} reported metric(s) could not be verified — add corresponding activity data")

        if not discrepancies and verified:
            recs.append("Reported figures align well with calculated estimates — no major concerns identified")

        return recs
