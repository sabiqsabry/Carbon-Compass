from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
  pass


class ReportStatus(str, Enum):
  PENDING = "pending"
  PROCESSING = "processing"
  COMPLETED = "completed"
  FAILED = "failed"


class Report(Base):
  __tablename__ = "reports"

  id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4,
  )
  filename: Mapped[str] = mapped_column(String, unique=True, nullable=False)
  company_name: Mapped[str | None] = mapped_column(String, nullable=True)
  report_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
  file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  upload_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
  status: Mapped[str] = mapped_column(String, default=ReportStatus.PENDING.value, index=True)

  analysis: Mapped[AnalysisResult] = relationship(
    back_populates="report",
    uselist=False,
    cascade="all, delete-orphan",
  )

  __table_args__ = (
    Index("ix_reports_filename", "filename"),
    Index("ix_reports_status", "status"),
  )


class AnalysisResult(Base):
  __tablename__ = "analysis_results"

  id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4,
  )
  report_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("reports.id", ondelete="CASCADE"),
    unique=True,
    index=True,
  )
  analysis_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
  processing_time_seconds: Mapped[float] = mapped_column(Float, default=0.0)
  raw_text_length: Mapped[int] = mapped_column(Integer, default=0)

  report: Mapped[Report] = relationship(back_populates="analysis")
  metrics: Mapped[list[ExtractedMetric]] = relationship(
    back_populates="analysis",
    cascade="all, delete-orphan",
  )
  greenwashing_flags: Mapped[list[GreenwashingFlag]] = relationship(
    back_populates="analysis",
    cascade="all, delete-orphan",
  )
  risk_score: Mapped[RiskScore | None] = relationship(
    back_populates="analysis",
    uselist=False,
    cascade="all, delete-orphan",
  )
  summary: Mapped[Summary | None] = relationship(
    back_populates="analysis",
    uselist=False,
    cascade="all, delete-orphan",
  )


class ExtractedMetric(Base):
  __tablename__ = "extracted_metrics"

  id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4,
  )
  analysis_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("analysis_results.id", ondelete="CASCADE"),
    index=True,
  )
  metric_type: Mapped[str] = mapped_column(String, index=True)
  value: Mapped[float] = mapped_column(Float)
  unit: Mapped[str] = mapped_column(String)
  year: Mapped[int | None] = mapped_column(Integer, nullable=True)
  scope: Mapped[str | None] = mapped_column(String, nullable=True)
  context: Mapped[str] = mapped_column(Text)
  confidence: Mapped[float] = mapped_column(Float)

  analysis: Mapped[AnalysisResult] = relationship(back_populates="metrics")


class GreenwashingFlag(Base):
  __tablename__ = "greenwashing_flags"

  id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4,
  )
  analysis_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("analysis_results.id", ondelete="CASCADE"),
    index=True,
  )
  indicator_type: Mapped[str] = mapped_column(String, index=True)
  flagged_text: Mapped[str] = mapped_column(Text)
  explanation: Mapped[str] = mapped_column(Text)
  severity: Mapped[str] = mapped_column(String)
  confidence: Mapped[float] = mapped_column(Float)

  analysis: Mapped[AnalysisResult] = relationship(back_populates="greenwashing_flags")


class RiskScore(Base):
  __tablename__ = "risk_scores"

  id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4,
  )
  analysis_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("analysis_results.id", ondelete="CASCADE"),
    unique=True,
    index=True,
  )
  overall_score: Mapped[float] = mapped_column(Float)
  risk_level: Mapped[str] = mapped_column(String)
  transparency_score: Mapped[float] = mapped_column(Float)
  commitment_score: Mapped[float] = mapped_column(Float)
  credibility_score: Mapped[float] = mapped_column(Float)
  data_quality_score: Mapped[float] = mapped_column(Float)
  verification_score: Mapped[float] = mapped_column(Float)
  recommendations: Mapped[list[str]] = mapped_column(JSON)

  analysis: Mapped[AnalysisResult] = relationship(back_populates="risk_score")


class Summary(Base):
  __tablename__ = "summaries"

  id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4,
  )
  analysis_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("analysis_results.id", ondelete="CASCADE"),
    unique=True,
    index=True,
  )
  executive_summary: Mapped[str] = mapped_column(Text)
  section_summaries: Mapped[dict] = mapped_column(JSON)
  commitments: Mapped[list[str]] = mapped_column(JSON)

  analysis: Mapped[AnalysisResult] = relationship(back_populates="summary")


class Calculation(Base):
    __tablename__ = "calculations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    total_emissions_kg: Mapped[float] = mapped_column(Float, default=0.0)
    scope_1_kg: Mapped[float] = mapped_column(Float, default=0.0)
    scope_2_kg: Mapped[float] = mapped_column(Float, default=0.0)
    scope_3_kg: Mapped[float] = mapped_column(Float, default=0.0)
    activity_count: Mapped[int] = mapped_column(Integer, default=0)
    source_file: Mapped[str | None] = mapped_column(String, nullable=True)

    activities: Mapped[list["CalculationActivity"]] = relationship(
        back_populates="calculation",
        cascade="all, delete-orphan",
    )
    verifications: Mapped[list["Verification"]] = relationship(
        back_populates="calculation",
        cascade="all, delete-orphan",
    )


class CalculationActivity(Base):
    __tablename__ = "calculation_activities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    calculation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("calculations.id", ondelete="CASCADE"),
        index=True,
    )
    category: Mapped[str] = mapped_column(String)
    sub_category: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    amount: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String)
    country: Mapped[str | None] = mapped_column(String, nullable=True)
    emissions_kg: Mapped[float] = mapped_column(Float, default=0.0)
    scope: Mapped[int] = mapped_column(Integer, default=3)
    factor_used: Mapped[float] = mapped_column(Float, default=0.0)

    calculation: Mapped["Calculation"] = relationship(back_populates="activities")


class Verification(Base):
    __tablename__ = "verifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="CASCADE"),
        index=True,
    )
    calculation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("calculations.id", ondelete="CASCADE"),
        index=True,
    )
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    discrepancy_count: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[str] = mapped_column(Text, default="")

    report: Mapped["Report"] = relationship()
    calculation: Mapped["Calculation"] = relationship(back_populates="verifications")
    discrepancies: Mapped[list["VerificationDiscrepancy"]] = relationship(
        back_populates="verification",
        cascade="all, delete-orphan",
    )


class VerificationDiscrepancy(Base):
    __tablename__ = "verification_discrepancies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    verification_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("verifications.id", ondelete="CASCADE"),
        index=True,
    )
    metric_type: Mapped[str] = mapped_column(String)
    reported_value: Mapped[float] = mapped_column(Float)
    calculated_value: Mapped[float] = mapped_column(Float)
    difference_percentage: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String)

    verification: Mapped["Verification"] = relationship(back_populates="discrepancies")

