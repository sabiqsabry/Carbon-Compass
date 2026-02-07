from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import Settings, get_settings
from ...models.database import get_session
from ...models.orm_models import AnalysisResult, ExtractedMetric, GreenwashingFlag, Report, RiskScore, Summary
from ...services.orchestrator import AnalysisOrchestrator


router = APIRouter(tags=["analysis"])


def get_orchestrator(settings: Settings = Depends(get_settings)) -> AnalysisOrchestrator:
    project_root = Path(__file__).resolve().parents[4]
    return AnalysisOrchestrator(project_root=project_root)


def _ensure_exists(filename: str, settings: Settings) -> None:
    path = settings.REPORTS_DIR / Path(filename).name
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")


def _serialise_analysis(result) -> Dict[str, Any]:
    return {
        "pdf": {
            "metadata": {
                "title": result.pdf.metadata.title,
                "author": result.pdf.metadata.author,
                "creation_date": result.pdf.metadata.creation_date,
                "modification_date": result.pdf.metadata.modification_date,
                "additional": result.pdf.metadata.additional,
            },
            "pages_count": len(result.pdf.pages),
            "sections": [
                {"name": s.name, "pages": s.pages, "length": len(s.text)} for s in result.pdf.sections
            ],
        },
        "chunks_count": result.chunks_count,
        "metrics": [
            {
                "metric_type": m.metric_type.value,
                "value": m.value,
                "unit": m.unit,
                "year": m.year,
                "scope": m.scope,
                "context": m.context,
                "confidence": m.confidence,
            }
            for m in result.metrics.metrics
        ],
        "greenwashing": {
            "risk_score": result.greenwashing.risk_score,
            "flags": [
                {
                    "indicator_type": f.indicator_type.value,
                    "text": f.text,
                    "explanation": f.explanation,
                    "severity": f.severity.value,
                    "confidence": f.confidence,
                }
                for f in result.greenwashing.flags
            ],
        },
        "summary": {
            "executive_summary": result.summary.executive_summary,
            "section_summaries": [
                {"section_name": s.section_name, "summary": s.summary}
                for s in result.summary.section_summaries
            ],
            "commitments": result.summary.commitments,
        },
        "risk": {
            "overall_score": result.risk.overall_score,
            "risk_level": result.risk.risk_level.value,
            "components": {
                "transparency": result.risk.components.transparency,
                "commitment": result.risk.components.commitment,
                "credibility": result.risk.components.credibility,
                "data_quality": result.risk.components.data_quality,
                "verification": result.risk.components.verification,
            },
            "recommendations": result.risk.recommendations,
        },
        "timings": result.timings,
    }


async def _save_analysis_to_db(filename: str, result, db: AsyncSession) -> None:
    """Save analysis results to database."""
    try:
        # Get or create report
        stmt = select(Report).where(Report.filename == filename)
        db_result = await db.execute(stmt)
        report = db_result.scalar_one_or_none()
        
        if not report:
            report = Report(filename=filename, uploaded_at=datetime.now(timezone.utc))
            db.add(report)
            await db.flush()
        
        # Create analysis result
        analysis = AnalysisResult(
            report_id=report.id,
            status="completed",
            analysed_at=datetime.now(timezone.utc),
            chunks_count=result.chunks_count,
            pages_count=len(result.pdf.pages),
        )
        db.add(analysis)
        await db.flush()
        
        # Save metrics
        for m in result.metrics.metrics:
            metric = ExtractedMetric(
                analysis_id=analysis.id,
                metric_type=m.metric_type.value,
                value=m.value,
                unit=m.unit,
                year=m.year,
                scope=m.scope,
                context=m.context,
                confidence=m.confidence,
            )
            db.add(metric)
        
        # Save greenwashing flags
        for f in result.greenwashing.flags:
            flag = GreenwashingFlag(
                analysis_id=analysis.id,
                indicator_type=f.indicator_type.value,
                text=f.text,
                explanation=f.explanation,
                severity=f.severity.value,
                confidence=f.confidence,
            )
            db.add(flag)
        
        # Save risk score
        risk = RiskScore(
            analysis_id=analysis.id,
            overall_score=result.risk.overall_score,
            risk_level=result.risk.risk_level.value,
            transparency=result.risk.components.transparency,
            commitment=result.risk.components.commitment,
            credibility=result.risk.components.credibility,
            data_quality=result.risk.components.data_quality,
            verification=result.risk.components.verification,
            recommendations=result.risk.recommendations,
        )
        db.add(risk)
        
        # Save summary
        summary = Summary(
            analysis_id=analysis.id,
            executive_summary=result.summary.executive_summary,
            section_summaries=[
                {"section_name": s.section_name, "summary": s.summary}
                for s in result.summary.section_summaries
            ],
            commitments=result.summary.commitments,
        )
        db.add(summary)
        
        await db.commit()
        print(f"✅ Saved analysis for {filename} to database")
    except Exception as e:
        print(f"⚠️  Failed to save analysis to database: {e}")
        await db.rollback()


async def _get_analysis_from_db(filename: str, db: AsyncSession) -> Dict[str, Any] | None:
    """Retrieve analysis results from database."""
    try:
        # Get report
        stmt = select(Report).where(Report.filename == filename)
        result = await db.execute(stmt)
        report = result.scalar_one_or_none()
        
        if not report:
            return None
        
        # Get latest analysis
        stmt = (
            select(AnalysisResult)
            .where(AnalysisResult.report_id == report.id)
            .where(AnalysisResult.status == "completed")
            .order_by(AnalysisResult.analysed_at.desc())
        )
        result = await db.execute(stmt)
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            return None
        
        # Get all related data
        metrics_stmt = select(ExtractedMetric).where(ExtractedMetric.analysis_id == analysis.id)
        metrics_result = await db.execute(metrics_stmt)
        metrics = metrics_result.scalars().all()
        
        flags_stmt = select(GreenwashingFlag).where(GreenwashingFlag.analysis_id == analysis.id)
        flags_result = await db.execute(flags_stmt)
        flags = flags_result.scalars().all()
        
        risk_stmt = select(RiskScore).where(RiskScore.analysis_id == analysis.id)
        risk_result = await db.execute(risk_stmt)
        risk = risk_result.scalar_one_or_none()
        
        summary_stmt = select(Summary).where(Summary.analysis_id == analysis.id)
        summary_result = await db.execute(summary_stmt)
        summary = summary_result.scalar_one_or_none()
        
        # Construct response
        return {
            "pdf": {
                "metadata": {},
                "pages_count": analysis.pages_count,
                "sections": [],
            },
            "chunks_count": analysis.chunks_count,
            "metrics": [
                {
                    "metric_type": m.metric_type,
                    "value": m.value,
                    "unit": m.unit,
                    "year": m.year,
                    "scope": m.scope,
                    "context": m.context,
                    "confidence": m.confidence,
                }
                for m in metrics
            ],
            "greenwashing": {
                "risk_score": sum(1 for f in flags),  # Simplified
                "flags": [
                    {
                        "indicator_type": f.indicator_type,
                        "text": f.text,
                        "explanation": f.explanation,
                        "severity": f.severity,
                        "confidence": f.confidence,
                    }
                    for f in flags
                ],
            },
            "summary": {
                "executive_summary": summary.executive_summary if summary else "",
                "section_summaries": summary.section_summaries if summary else [],
                "commitments": summary.commitments if summary else [],
            },
            "risk": {
                "overall_score": risk.overall_score if risk else 0,
                "risk_level": risk.risk_level if risk else "UNKNOWN",
                "components": {
                    "transparency": risk.transparency if risk else 0,
                    "commitment": risk.commitment if risk else 0,
                    "credibility": risk.credibility if risk else 0,
                    "data_quality": risk.data_quality if risk else 0,
                    "verification": risk.verification if risk else 0,
                } if risk else {},
                "recommendations": risk.recommendations if risk else [],
            },
            "timings": {},
        }
    except Exception as e:
        print(f"⚠️  Failed to fetch analysis from database: {e}")
        return None


@router.post("/analyse/{filename}")
async def analyse_report(
    filename: str,
    settings: Settings = Depends(get_settings),
    orchestrator: AnalysisOrchestrator = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Run analysis on a report and save results to database."""
    _ensure_exists(filename, settings)
    result = orchestrator.analyse(Path(filename).name)
    
    # Save to database
    await _save_analysis_to_db(Path(filename).name, result, db)
    
    return _serialise_analysis(result)


@router.get("/analysis/{filename}")
async def get_analysis(
    filename: str,
    settings: Settings = Depends(get_settings),
    orchestrator: AnalysisOrchestrator = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Get analysis results (from database if available, otherwise run analysis)."""
    _ensure_exists(filename, settings)
    
    # Try to get from database first
    db_result = await _get_analysis_from_db(Path(filename).name, db)
    if db_result:
        print(f"📊 Retrieved analysis for {filename} from database")
        return db_result
    
    # Run analysis if not in database
    print(f"🔄 Running fresh analysis for {filename}")
    result = orchestrator.analyse(Path(filename).name)
    await _save_analysis_to_db(Path(filename).name, result, db)
    return _serialise_analysis(result)


@router.get("/analysis/{filename}/metrics")
async def get_metrics(
    filename: str,
    settings: Settings = Depends(get_settings),
    orchestrator: AnalysisOrchestrator = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_session),
) -> List[Dict[str, Any]]:
    """Get extracted metrics for a report."""
    _ensure_exists(filename, settings)
    
    # Try database first
    db_result = await _get_analysis_from_db(Path(filename).name, db)
    if db_result:
        return db_result["metrics"]
    
    # Fallback to orchestrator
    result = orchestrator.analyse(Path(filename).name)
    await _save_analysis_to_db(Path(filename).name, result, db)
    return [
        {
            "metric_type": m.metric_type.value,
            "value": m.value,
            "unit": m.unit,
            "year": m.year,
            "scope": m.scope,
            "context": m.context,
            "confidence": m.confidence,
        }
        for m in result.metrics.metrics
    ]


@router.get("/analysis/{filename}/greenwashing")
async def get_greenwashing(
    filename: str,
    settings: Settings = Depends(get_settings),
    orchestrator: AnalysisOrchestrator = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Get greenwashing analysis for a report."""
    _ensure_exists(filename, settings)
    
    # Try database first
    db_result = await _get_analysis_from_db(Path(filename).name, db)
    if db_result:
        return db_result["greenwashing"]
    
    # Fallback to orchestrator
    result = orchestrator.analyse(Path(filename).name)
    await _save_analysis_to_db(Path(filename).name, result, db)
    return {
        "risk_score": result.greenwashing.risk_score,
        "flags": [
            {
                "indicator_type": f.indicator_type.value,
                "text": f.text,
                "explanation": f.explanation,
                "severity": f.severity.value,
                "confidence": f.confidence,
            }
            for f in result.greenwashing.flags
        ],
    }


@router.get("/analysis/{filename}/summary")
async def get_summary(
    filename: str,
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Get summary for a report with generation status.

    Returns ``status``: ``"completed"`` if summaries have been generated,
    ``"pending"`` if summarisation has not run yet.
    """
    _ensure_exists(filename, settings)

    # Check DB for existing summary
    clean_name = Path(filename).name
    try:
        stmt = select(Report).where(Report.filename == clean_name)
        result = await db.execute(stmt)
        report = result.scalar_one_or_none()

        if report:
            analysis_stmt = (
                select(AnalysisResult)
                .where(AnalysisResult.report_id == report.id)
                .where(AnalysisResult.status == "completed")
                .order_by(AnalysisResult.analysed_at.desc())
            )
            analysis_result = await db.execute(analysis_stmt)
            analysis = analysis_result.scalar_one_or_none()

            if analysis:
                summary_stmt = select(Summary).where(Summary.analysis_id == analysis.id)
                summary_result = await db.execute(summary_stmt)
                summary = summary_result.scalar_one_or_none()

                if summary and (summary.executive_summary or summary.section_summaries):
                    return {
                        "status": "completed",
                        "executive_summary": summary.executive_summary,
                        "section_summaries": summary.section_summaries or [],
                        "commitments": summary.commitments or [],
                    }
    except Exception as e:
        print(f"⚠️  Failed to check summary in database: {e}")

    return {
        "status": "pending",
        "executive_summary": "",
        "section_summaries": [],
        "commitments": [],
    }


@router.post("/analysis/{filename}/summarise")
async def generate_summary(
    filename: str,
    settings: Settings = Depends(get_settings),
    orchestrator: AnalysisOrchestrator = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Trigger summarisation for a report (runs the BART model).

    This is intentionally a separate endpoint so the main analysis can
    return quickly while summarisation runs in the background.  The heavy
    model inference is offloaded to a thread so it doesn't block the
    event loop.
    """
    _ensure_exists(filename, settings)
    clean_name = Path(filename).name

    # Run the CPU-heavy summarisation in a thread pool
    summary_result = await asyncio.to_thread(orchestrator.summarise, clean_name)

    # Persist to database
    try:
        stmt = select(Report).where(Report.filename == clean_name)
        result = await db.execute(stmt)
        report = result.scalar_one_or_none()

        if report:
            analysis_stmt = (
                select(AnalysisResult)
                .where(AnalysisResult.report_id == report.id)
                .where(AnalysisResult.status == "completed")
                .order_by(AnalysisResult.analysed_at.desc())
            )
            analysis_result = await db.execute(analysis_stmt)
            analysis = analysis_result.scalar_one_or_none()

            if analysis:
                # Update or create summary record
                summary_stmt = select(Summary).where(Summary.analysis_id == analysis.id)
                summary_db_result = await db.execute(summary_stmt)
                existing_summary = summary_db_result.scalar_one_or_none()

                section_data = [
                    {"section_name": s.section_name, "summary": s.summary}
                    for s in summary_result.section_summaries
                ]
                commitments_data = summary_result.commitments

                if existing_summary:
                    existing_summary.executive_summary = summary_result.executive_summary
                    existing_summary.section_summaries = section_data
                    existing_summary.commitments = commitments_data
                else:
                    new_summary = Summary(
                        analysis_id=analysis.id,
                        executive_summary=summary_result.executive_summary,
                        section_summaries=section_data,
                        commitments=commitments_data,
                    )
                    db.add(new_summary)

                await db.commit()
                print(f"✅ Saved summary for {clean_name} to database")
    except Exception as e:
        print(f"⚠️  Failed to save summary to database: {e}")
        await db.rollback()

    return {
        "status": "completed",
        "executive_summary": summary_result.executive_summary,
        "section_summaries": [
            {"section_name": s.section_name, "summary": s.summary}
            for s in summary_result.section_summaries
        ],
        "commitments": summary_result.commitments,
    }


@router.get("/analysis/{filename}/risk")
async def get_risk(
    filename: str,
    settings: Settings = Depends(get_settings),
    orchestrator: AnalysisOrchestrator = Depends(get_orchestrator),
    db: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Get risk score for a report."""
    _ensure_exists(filename, settings)
    
    # Try database first
    db_result = await _get_analysis_from_db(Path(filename).name, db)
    if db_result:
        return db_result["risk"]
    
    # Fallback to orchestrator
    result = orchestrator.analyse(Path(filename).name)
    await _save_analysis_to_db(Path(filename).name, result, db)
    return {
        "overall_score": result.risk.overall_score,
        "risk_level": result.risk.risk_level.value,
        "components": {
            "transparency": result.risk.components.transparency,
            "commitment": result.risk.components.commitment,
            "credibility": result.risk.components.credibility,
            "data_quality": result.risk.components.data_quality,
            "verification": result.risk.components.verification,
        },
        "recommendations": result.risk.recommendations,
    }
