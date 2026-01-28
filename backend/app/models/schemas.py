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

