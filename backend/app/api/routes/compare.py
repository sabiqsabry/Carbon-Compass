from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...core.config import Settings, get_settings
from ...services.orchestrator import AnalysisOrchestrator


router = APIRouter(tags=["compare"])


class CompareRequest(BaseModel):
  filenames: List[str] = Field(min_length=2, max_length=4, description="List of report filenames to compare")


def get_orchestrator(settings: Settings = Depends(get_settings)) -> AnalysisOrchestrator:
  project_root = Path(__file__).resolve().parents[4]
  return AnalysisOrchestrator(project_root=project_root)


def _ensure_all_exist(filenames: List[str], settings: Settings) -> None:
  missing: List[str] = []
  for name in filenames:
    if not (settings.REPORTS_DIR / Path(name).name).exists():
      missing.append(name)
  if missing:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Reports not found: {', '.join(missing)}",
    )


@router.post("/compare")
async def compare_reports(
  payload: CompareRequest,
  settings: Settings = Depends(get_settings),
  orchestrator: AnalysisOrchestrator = Depends(get_orchestrator),
) -> Dict[str, Any]:
  _ensure_all_exist(payload.filenames, settings)

  results = {name: orchestrator.analyse(Path(name).name) for name in payload.filenames}

  comparison = {
    "companies": list(results.keys()),
    "risk": {
      name: {
        "overall_score": r.risk.overall_score,
        "risk_level": r.risk.risk_level.value,
        "components": {
          "transparency": r.risk.components.transparency,
          "commitment": r.risk.components.commitment,
          "credibility": r.risk.components.credibility,
          "data_quality": r.risk.components.data_quality,
          "verification": r.risk.components.verification,
        },
      }
      for name, r in results.items()
    },
    "greenwashing": {
      name: {
        "risk_score": r.greenwashing.risk_score,
        "flags_count": len(r.greenwashing.flags),
      }
      for name, r in results.items()
    },
  }

  return comparison

