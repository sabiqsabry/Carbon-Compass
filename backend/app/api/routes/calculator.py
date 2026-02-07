"""Calculator API routes for the Structured Data route."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.database import get_session
from ...models.orm_models import Calculation, CalculationActivity
from ...services.activity_parser import ActivityParser
from ...services.emissions_calculator import ActivityInput, EmissionsCalculator
from ...services.factor_loader import FactorLoader


router = APIRouter(tags=["calculator"])

# Lazy-init singletons
_calculator: EmissionsCalculator | None = None
_parser: ActivityParser | None = None
_loader: FactorLoader | None = None


def _get_calculator() -> EmissionsCalculator:
    global _calculator
    if _calculator is None:
        _calculator = EmissionsCalculator()
    return _calculator


def _get_parser() -> ActivityParser:
    global _parser
    if _parser is None:
        _parser = ActivityParser()
    return _parser


def _get_loader() -> FactorLoader:
    global _loader
    if _loader is None:
        _loader = FactorLoader()
    return _loader


# ── Request / Response Models ────────────────────────────────

class SingleActivityRequest(BaseModel):
    category: str = Field(..., description="Activity category: electricity, fuel, transport, flight, waste, water")
    sub_category: Optional[str] = Field(None, description="Sub-category (e.g. diesel, short_haul)")
    amount: float = Field(..., gt=0, description="Activity amount")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    country: Optional[str] = Field(None, description="Country (for electricity)")
    flight_class: Optional[str] = Field(None, description="Flight class (economy, business, first)")
    return_trip: bool = Field(False, description="Whether this is a return trip (flights)")


class BulkActivityRequest(BaseModel):
    activities: List[SingleActivityRequest] = Field(..., min_length=1, description="List of activities")


class ColumnMappingRequest(BaseModel):
    column_mapping: Optional[Dict[str, str]] = Field(None, description="Manual column mapping override")


# ── Routes ───────────────────────────────────────────────────

@router.post("/calculate/single")
async def calculate_single(request: SingleActivityRequest) -> Dict[str, Any]:
    """Calculate emissions for a single activity.

    Returns the emission result with scope classification and calculation details.
    """
    calculator = _get_calculator()

    try:
        activity = ActivityInput(
            category=request.category,
            sub_category=request.sub_category,
            amount=request.amount,
            unit=request.unit or "",
            country=request.country,
            flight_class=request.flight_class,
            return_trip=request.return_trip,
        )
        result = calculator.calculate_single(activity)
        return result.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/calculate/bulk")
async def calculate_bulk(request: BulkActivityRequest) -> Dict[str, Any]:
    """Calculate emissions for multiple activities.

    Returns total emissions with scope and category breakdowns.
    """
    calculator = _get_calculator()

    try:
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
        result = calculator.calculate_total(activities)
        return result.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/calculate/upload")
async def calculate_from_upload(
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    """Upload a CSV or Excel file and calculate emissions.

    Accepts .csv, .xlsx, .xls files with activity data.
    Returns total emissions plus any parsing warnings.
    """
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("csv", "xlsx", "xls"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file format: .{ext}. Use .csv, .xlsx, or .xls",
        )

    parser = _get_parser()
    calculator = _get_calculator()

    try:
        content = await file.read()

        if ext == "csv":
            activities = parser.parse_csv(content)
        else:
            activities = parser.parse_excel(content)

        validation = parser.validate_activities(activities)

        if not validation.valid_activities:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "No valid activities found in file",
                    "errors": validation.errors,
                    "warnings": validation.warnings,
                },
            )

        result = calculator.calculate_total(validation.valid_activities)
        response = result.to_dict()
        response["parsing"] = {
            "total_rows": len(activities),
            "valid_rows": len(validation.valid_activities),
            "invalid_rows": len(validation.invalid_rows),
            "errors": validation.errors,
            "warnings": validation.warnings + result.warnings,
        }
        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse file: {str(e)}",
        )


@router.post("/calculate/upload/preview")
async def preview_upload(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Preview an uploaded file before calculating.

    Returns column headers, first 5 rows, and auto-detected column mapping.
    """
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("csv", "xlsx", "xls"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file format: .{ext}",
        )

    parser = _get_parser()

    try:
        content = await file.read()
        file_type = "csv" if ext == "csv" else "excel"
        return parser.get_file_preview(content, file_type=file_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to preview file: {str(e)}",
        )


@router.get("/calculate/factors")
async def list_factors(
    category: Optional[str] = Query(None, description="Filter by category: electricity, fuel, transport, waste, water"),
) -> Dict[str, Any]:
    """List all available emission factors.

    Optionally filter by category.
    """
    loader = _get_loader()

    result: Dict[str, Any] = {}

    if category is None or category == "electricity":
        result["electricity"] = loader.list_available_countries()
    if category is None or category == "fuel":
        result["fuel"] = loader.list_available_fuels()
    if category is None or category == "transport":
        result["transport"] = loader.list_available_transport()
    if category is None or category == "waste":
        result["waste"] = loader.list_available_waste_methods()
    if category is None or category == "water":
        water_data = {
            "supply": {"value": loader.get_water_factor("supply"), "unit": "kg CO2e/m³"},
            "treatment": {"value": loader.get_water_factor("treatment"), "unit": "kg CO2e/m³"},
            "supply_and_treatment": {"value": loader.get_water_factor("supply_and_treatment"), "unit": "kg CO2e/m³"},
        }
        result["water"] = water_data

    return result


@router.get("/calculate/countries")
async def list_countries() -> List[Dict[str, Any]]:
    """List all countries with available electricity emission factors."""
    loader = _get_loader()
    return loader.list_available_countries()


# ── Persistence Routes ───────────────────────────────────────

@router.post("/calculate/save")
async def save_calculation(
    request: BulkActivityRequest,
    name: Optional[str] = Query(None, description="Optional name for this calculation"),
    db: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Calculate and save emissions to the database.

    Persists the calculation and all activity line items for later retrieval.
    """
    calculator = _get_calculator()

    try:
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
        result = calculator.calculate_total(activities)

        # Save to database
        calc = Calculation(
            name=name,
            total_emissions_kg=result.total_kg_co2e,
            scope_1_kg=result.by_scope.get("scope_1", 0),
            scope_2_kg=result.by_scope.get("scope_2", 0),
            scope_3_kg=result.by_scope.get("scope_3", 0),
            activity_count=result.activity_count,
        )
        db.add(calc)
        await db.flush()

        for r in result.breakdown:
            activity = CalculationActivity(
                calculation_id=calc.id,
                category=r.activity_type,
                sub_category=None,
                amount=r.activity_amount,
                unit=r.activity_unit,
                emissions_kg=r.emissions_kg_co2e,
                scope=r.scope,
                factor_used=r.factor_used,
            )
            db.add(activity)

        await db.commit()

        response = result.to_dict()
        response["calculation_id"] = str(calc.id)
        return response

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/calculations")
async def list_calculations(
    db: AsyncSession = Depends(get_session),
) -> List[Dict[str, Any]]:
    """List all saved calculations."""
    stmt = select(Calculation).order_by(Calculation.created_at.desc())
    result = await db.execute(stmt)
    calculations = result.scalars().all()

    return [
        {
            "id": str(c.id),
            "name": c.name,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "total_emissions_kg": c.total_emissions_kg,
            "total_emissions_tonnes": c.total_emissions_kg / 1000,
            "scope_1_kg": c.scope_1_kg,
            "scope_2_kg": c.scope_2_kg,
            "scope_3_kg": c.scope_3_kg,
            "activity_count": c.activity_count,
            "source_file": c.source_file,
        }
        for c in calculations
    ]


@router.get("/calculations/{calculation_id}")
async def get_calculation(
    calculation_id: str,
    db: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Get a saved calculation with its activity breakdown."""
    import uuid as uuid_mod
    try:
        calc_uuid = uuid_mod.UUID(calculation_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid calculation ID")

    stmt = select(Calculation).where(Calculation.id == calc_uuid)
    result = await db.execute(stmt)
    calc = result.scalar_one_or_none()

    if not calc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation not found")

    # Get activities
    activities_stmt = select(CalculationActivity).where(
        CalculationActivity.calculation_id == calc.id
    )
    activities_result = await db.execute(activities_stmt)
    activities = activities_result.scalars().all()

    return {
        "id": str(calc.id),
        "name": calc.name,
        "created_at": calc.created_at.isoformat() if calc.created_at else None,
        "total_emissions_kg": calc.total_emissions_kg,
        "total_emissions_tonnes": calc.total_emissions_kg / 1000,
        "scope_1_kg": calc.scope_1_kg,
        "scope_2_kg": calc.scope_2_kg,
        "scope_3_kg": calc.scope_3_kg,
        "activity_count": calc.activity_count,
        "source_file": calc.source_file,
        "by_scope": {
            "scope_1": calc.scope_1_kg,
            "scope_2": calc.scope_2_kg,
            "scope_3": calc.scope_3_kg,
        },
        "activities": [
            {
                "id": str(a.id),
                "category": a.category,
                "sub_category": a.sub_category,
                "amount": a.amount,
                "unit": a.unit,
                "country": a.country,
                "emissions_kg": a.emissions_kg,
                "scope": a.scope,
                "factor_used": a.factor_used,
            }
            for a in activities
        ],
    }
