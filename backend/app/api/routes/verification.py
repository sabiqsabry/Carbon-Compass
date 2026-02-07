"""Verification API routes for comparing NLP vs calculated emissions."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import Settings, get_settings
from ...models.database import get_session
from ...models.orm_models import AnalysisResult, ExtractedMetric, Report
from ...services.activity_parser import ActivityParser
from ...services.emissions_calculator import ActivityInput, EmissionsCalculator
from ...services.verification_engine import ExtractedMetricData, VerificationEngine


router = APIRouter(tags=["verification"])


class VerifyActivityRequest(BaseModel):
    category: str
    sub_category: Optional[str] = None
    amount: float = Field(..., gt=0)
    unit: Optional[str] = None
    country: Optional[str] = None
    flight_class: Optional[str] = None
    return_trip: bool = False


class VerifyRequest(BaseModel):
    activities: List[VerifyActivityRequest] = Field(..., min_length=1)


@router.post("/verify/{report_filename}")
async def verify_report(
    report_filename: str,
    request: VerifyRequest,
    db: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Compare NLP analysis of a report against calculated emissions.

    Takes activity data and compares the calculated emissions against
    the metrics extracted from the specified report by the NLP route.
    """
    # Get the report and its metrics from the database
    stmt = select(Report).where(Report.filename == report_filename)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_filename}' not found. Upload and analyse it first.",
        )

    # Get the latest analysis
    analysis_stmt = (
        select(AnalysisResult)
        .where(AnalysisResult.report_id == report.id)
        .order_by(AnalysisResult.analysis_date.desc())
    )
    analysis_result = await db.execute(analysis_stmt)
    analysis = analysis_result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No analysis found for '{report_filename}'. Run analysis first.",
        )

    # Get extracted metrics
    metrics_stmt = select(ExtractedMetric).where(ExtractedMetric.analysis_id == analysis.id)
    metrics_result = await db.execute(metrics_stmt)
    metrics = metrics_result.scalars().all()

    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No metrics found in the analysis. The NLP route may not have extracted any.",
        )

    # Calculate emissions from activity data
    calculator = EmissionsCalculator()
    activities = [
        ActivityInput(
            category=a.category,
            sub_category=a.sub_category,
            amount=a.amount,
            unit=a.unit or "",
            country=a.country,
            flight_class=a.flight_class,
            return_trip=a.return_trip,
        )
        for a in request.activities
    ]
    calculated = calculator.calculate_total(activities)

    # Convert NLP metrics to comparison format
    nlp_metrics = [
        ExtractedMetricData(
            metric_type=m.metric_type,
            value=m.value,
            unit=m.unit,
            scope=m.scope,
            confidence=m.confidence,
        )
        for m in metrics
    ]

    # Run verification
    engine = VerificationEngine()
    verification = engine.compare(
        nlp_metrics=nlp_metrics,
        calculated_by_scope=calculated.by_scope,
        calculated_total_kg=calculated.total_kg_co2e,
        calculated_by_category=calculated.by_category,
    )

    return {
        "report": report_filename,
        "verification": verification.to_dict(),
        "calculated_emissions": calculated.to_dict(),
    }


@router.get("/verify/{report_filename}/summary")
async def verify_summary(
    report_filename: str,
    db: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Get a quick summary of what NLP extracted from a report.

    Shows the metrics available for verification.
    """
    stmt = select(Report).where(Report.filename == report_filename)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_filename}' not found.",
        )

    analysis_stmt = (
        select(AnalysisResult)
        .where(AnalysisResult.report_id == report.id)
        .order_by(AnalysisResult.analysis_date.desc())
    )
    analysis_result = await db.execute(analysis_stmt)
    analysis = analysis_result.scalar_one_or_none()

    if not analysis:
        return {"report": report_filename, "has_analysis": False, "metrics": []}

    metrics_stmt = select(ExtractedMetric).where(ExtractedMetric.analysis_id == analysis.id)
    metrics_result = await db.execute(metrics_stmt)
    metrics = metrics_result.scalars().all()

    return {
        "report": report_filename,
        "has_analysis": True,
        "metrics_count": len(metrics),
        "metrics": [
            {
                "metric_type": m.metric_type,
                "value": m.value,
                "unit": m.unit,
                "scope": m.scope,
                "confidence": m.confidence,
            }
            for m in metrics
        ],
    }


@router.get("/verifications")
async def list_verifications(
    db: AsyncSession = Depends(get_session),
) -> List[Dict[str, Any]]:
    """List all past verification results."""
    from ...models.orm_models import Verification as VerificationModel

    stmt = select(VerificationModel).order_by(VerificationModel.verified_at.desc())
    result = await db.execute(stmt)
    verifications = result.scalars().all()

    return [
        {
            "id": str(v.id),
            "report_id": str(v.report_id),
            "calculation_id": str(v.calculation_id),
            "verified_at": v.verified_at.isoformat() if v.verified_at else None,
            "match_score": v.match_score,
            "discrepancy_count": v.discrepancy_count,
            "summary": v.summary,
        }
        for v in verifications
    ]
