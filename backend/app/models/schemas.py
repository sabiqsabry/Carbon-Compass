from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ReportInfo(BaseModel):
  filename: str
  size_bytes: Optional[int] = None


class UploadResponse(BaseModel):
  file_id: str
  filename: str


class MetricModel(BaseModel):
  metric_type: str
  value: float
  unit: str
  year: Optional[int] = None
  scope: Optional[str] = None
  context: str
  confidence: float


class GreenwashingFlagModel(BaseModel):
  indicator_type: str
  text: str
  explanation: str
  severity: str
  confidence: float


class GreenwashingModel(BaseModel):
  risk_score: float
  flags: List[GreenwashingFlagModel]


class SectionSummaryModel(BaseModel):
  section_name: str
  summary: str


class SummaryModel(BaseModel):
  executive_summary: str
  section_summaries: List[SectionSummaryModel]
  commitments: List[str]


class RiskComponentsModel(BaseModel):
  transparency: float
  commitment: float
  credibility: float
  data_quality: float
  verification: float


class RiskModel(BaseModel):
  overall_score: float
  risk_level: str
  components: RiskComponentsModel
  recommendations: List[str]


class AnalysisMetadataModel(BaseModel):
  title: Optional[str] = None
  author: Optional[str] = None
  creation_date: Optional[str] = None
  modification_date: Optional[str] = None
  additional: dict = Field(default_factory=dict)


class PdfInfoModel(BaseModel):
  metadata: AnalysisMetadataModel
  pages_count: int
  sections: List[dict]


class AnalysisResponse(BaseModel):
  pdf: PdfInfoModel
  chunks_count: int
  metrics: List[MetricModel]
  greenwashing: GreenwashingModel
  summary: SummaryModel
  risk: RiskModel
  timings: dict


class HealthResponse(BaseModel):
  status: str
  timestamp: datetime


# ── Structured Data Route Models ─────────────────────────────

class ActivityInputSchema(BaseModel):
    category: str
    sub_category: Optional[str] = None
    description: Optional[str] = None
    amount: float
    unit: str = ""
    country: Optional[str] = None
    date: Optional[str] = None
    flight_class: Optional[str] = None
    return_trip: bool = False


class EmissionResultResponse(BaseModel):
    activity_type: str
    activity_amount: float
    activity_unit: str
    emissions_kg_co2e: float
    emissions_tonnes_co2e: float
    scope: int
    factor_used: float
    factor_source: str
    calculation_details: str


class TotalEmissionsResponse(BaseModel):
    total_kg_co2e: float
    total_tonnes_co2e: float
    by_scope: dict
    by_category: dict
    breakdown: List[EmissionResultResponse]
    activity_count: int
    warnings: List[str] = Field(default_factory=list)


class DiscrepancyResponse(BaseModel):
    metric_type: str
    reported_value: float
    reported_unit: str
    calculated_value: float
    calculated_unit: str
    difference_absolute: float
    difference_percentage: float
    severity: str
    possible_explanations: List[str]


class VerificationResultResponse(BaseModel):
    match_score: float
    discrepancies: List[DiscrepancyResponse]
    summary: str
    recommendations: List[str]
    data_completeness: float


class FactorListResponse(BaseModel):
    electricity: Optional[list] = None
    fuel: Optional[list] = None
    transport: Optional[dict] = None
    waste: Optional[dict] = None
    water: Optional[dict] = None

