from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import Settings, get_settings
from ...models.database import get_session
from ...models.orm_models import Report


router = APIRouter(tags=["upload"])


def _ensure_reports_dir(reports_dir: Path) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_session),
) -> dict:
    """Upload a PDF sustainability report."""
    # Basic validation
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed.",
        )

    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File is too large. Maximum size is {settings.MAX_FILE_SIZE // (1024 * 1024)}MB.",
        )

    # Save file to disk
    _ensure_reports_dir(settings.REPORTS_DIR)
    filename = file.filename or "report.pdf"
    safe_name = Path(filename).name
    dest_path = settings.REPORTS_DIR / safe_name

    dest_path.write_bytes(contents)

    # Save to database
    try:
        # Check if report already exists
        stmt = select(Report).where(Report.filename == safe_name)
        result = await db.execute(stmt)
        existing_report = result.scalar_one_or_none()

        if existing_report:
            # Update existing report
            existing_report.size_bytes = len(contents)
            existing_report.uploaded_at = datetime.now(timezone.utc)
        else:
            # Create new report
            report = Report(
                filename=safe_name,
                size_bytes=len(contents),
                uploaded_at=datetime.now(timezone.utc),
            )
            db.add(report)

        await db.commit()
    except Exception as e:
        # If database fails, continue without it (file is already saved)
        print(f"⚠️  Failed to save report to database: {e}")

    return {
        "file_id": safe_name,
        "filename": safe_name,
    }


@router.get("/reports")
async def list_reports(
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_session),
) -> List[dict]:
    """List all uploaded reports."""
    _ensure_reports_dir(settings.REPORTS_DIR)
    
    try:
        # Try to fetch from database first
        stmt = select(Report).order_by(Report.uploaded_at.desc())
        result = await db.execute(stmt)
        reports_from_db = result.scalars().all()
        
        if reports_from_db:
            return [
                {
                    "filename": report.filename,
                    "size_bytes": report.size_bytes,
                    "uploaded_at": report.uploaded_at.isoformat() if report.uploaded_at else None,
                }
                for report in reports_from_db
            ]
    except Exception as e:
        print(f"⚠️  Failed to fetch reports from database: {e}")
    
    # Fallback to file system
    reports: List[dict] = []
    for path in sorted(settings.REPORTS_DIR.glob("*.pdf")):
        try:
            size = path.stat().st_size
        except OSError:
            size = None
        reports.append(
            {
                "filename": path.name,
                "size_bytes": size,
            }
        )
    return reports


@router.get("/reports/{filename}")
async def get_report(
    filename: str,
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_session),
) -> dict:
    """Get information about a specific report."""
    _ensure_reports_dir(settings.REPORTS_DIR)
    target = settings.REPORTS_DIR / Path(filename).name
    
    if not target.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    
    try:
        # Try to fetch from database first
        stmt = select(Report).where(Report.filename == Path(filename).name)
        result = await db.execute(stmt)
        report = result.scalar_one_or_none()
        
        if report:
            return {
                "filename": report.filename,
                "size_bytes": report.size_bytes,
                "uploaded_at": report.uploaded_at.isoformat() if report.uploaded_at else None,
            }
    except Exception as e:
        print(f"⚠️  Failed to fetch report from database: {e}")
    
    # Fallback to file system
    try:
        size = target.stat().st_size
    except OSError:
        size = None
    
    return {
        "filename": target.name,
        "size_bytes": size,
    }

