"""Core emissions calculator service for Carbon Compass.

Calculates greenhouse gas emissions from activity data using official
conversion factors (UK DEFRA 2024, IEA).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .factor_loader import FactorLoader, FactorNotFoundError


@dataclass
class EmissionResult:
    """Result of a single emission calculation."""
    activity_type: str
    activity_amount: float
    activity_unit: str
    emissions_kg_co2e: float
    emissions_tonnes_co2e: float
    scope: int
    factor_used: float
    factor_source: str
    calculation_details: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "activity_type": self.activity_type,
            "activity_amount": self.activity_amount,
            "activity_unit": self.activity_unit,
            "emissions_kg_co2e": round(self.emissions_kg_co2e, 2),
            "emissions_tonnes_co2e": round(self.emissions_tonnes_co2e, 6),
            "scope": self.scope,
            "factor_used": self.factor_used,
            "factor_source": self.factor_source,
            "calculation_details": self.calculation_details,
        }


@dataclass
class ActivityInput:
    """Input for a single activity to calculate emissions for."""
    category: str  # electricity, fuel, transport, waste, water
    sub_category: Optional[str] = None
    description: Optional[str] = None
    amount: float = 0.0
    unit: str = ""
    country: Optional[str] = None
    date: Optional[str] = None
    flight_class: Optional[str] = None
    return_trip: bool = False
    raw_row: Optional[Dict[str, Any]] = None


@dataclass
class TotalEmissions:
    """Result of a bulk emission calculation."""
    total_kg_co2e: float
    total_tonnes_co2e: float
    by_scope: Dict[str, float]  # {"scope_1": ..., "scope_2": ..., "scope_3": ...}
    by_category: Dict[str, float]  # {"electricity": ..., "fuel": ..., etc.}
    breakdown: List[EmissionResult]
    activity_count: int
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_kg_co2e": round(self.total_kg_co2e, 2),
            "total_tonnes_co2e": round(self.total_tonnes_co2e, 6),
            "by_scope": {k: round(v, 2) for k, v in self.by_scope.items()},
            "by_category": {k: round(v, 2) for k, v in self.by_category.items()},
            "breakdown": [r.to_dict() for r in self.breakdown],
            "activity_count": self.activity_count,
            "warnings": self.warnings,
        }


class EmissionsCalculator:
    """Calculates greenhouse gas emissions from activity data.

    Uses official conversion factors from UK DEFRA 2024 and IEA.
    """

    def __init__(self, factor_loader: Optional[FactorLoader] = None) -> None:
        self._loader = factor_loader or FactorLoader()

    def calculate_electricity(
        self,
        kwh: float,
        country: str = "world_average",
        renewable_percentage: float = 0,
    ) -> EmissionResult:
        """Calculate emissions from electricity consumption.

        Args:
            kwh: Electricity consumed in kilowatt-hours.
            country: Country for grid emission factor.
            renewable_percentage: Percentage of electricity from renewable sources (0-100).

        Returns:
            EmissionResult with Scope 2 classification.
        """
        self._validate_positive(kwh, "electricity kWh")
        if not 0 <= renewable_percentage <= 100:
            raise ValueError("Renewable percentage must be between 0 and 100.")

        factor = self._loader.get_electricity_factor(country)
        grid_kwh = kwh * (1 - renewable_percentage / 100)
        emissions_kg = grid_kwh * factor

        return EmissionResult(
            activity_type="electricity",
            activity_amount=kwh,
            activity_unit="kWh",
            emissions_kg_co2e=emissions_kg,
            emissions_tonnes_co2e=emissions_kg / 1000,
            scope=2,
            factor_used=factor,
            factor_source=f"IEA/DEFRA 2024 - {country}",
            calculation_details=(
                f"{kwh:,.0f} kWh × {factor} kg CO2e/kWh"
                + (f" × {(100 - renewable_percentage):.0f}% grid" if renewable_percentage > 0 else "")
                + f" = {emissions_kg:,.2f} kg CO2e"
            ),
        )

    def calculate_fuel(
        self,
        amount: float,
        fuel_type: str,
        unit: str = "litres",
    ) -> EmissionResult:
        """Calculate emissions from fuel combustion.

        Args:
            amount: Amount of fuel.
            fuel_type: Type of fuel (petrol, diesel, natural_gas, etc.).
            unit: Unit of measurement.

        Returns:
            EmissionResult with Scope 1 classification.
        """
        self._validate_positive(amount, f"fuel amount ({fuel_type})")

        factor = self._loader.get_fuel_factor(fuel_type, unit)
        scope = self._loader.get_fuel_scope(fuel_type)
        emissions_kg = amount * factor

        return EmissionResult(
            activity_type="fuel",
            activity_amount=amount,
            activity_unit=unit,
            emissions_kg_co2e=emissions_kg,
            emissions_tonnes_co2e=emissions_kg / 1000,
            scope=scope,
            factor_used=factor,
            factor_source=f"UK DEFRA 2024 - {fuel_type}",
            calculation_details=(
                f"{amount:,.2f} {unit} of {fuel_type} × {factor} kg CO2e/{unit} = {emissions_kg:,.2f} kg CO2e"
            ),
        )

    def calculate_transport(
        self,
        distance: float,
        mode: str,
        vehicle_type: Optional[str] = None,
        passengers: int = 1,
        unit: str = "km",
    ) -> EmissionResult:
        """Calculate emissions from ground transport.

        Args:
            distance: Distance travelled.
            mode: Transport mode (road, rail).
            vehicle_type: Specific vehicle type.
            passengers: Number of passengers (for per-person allocation).
            unit: Distance unit ('km' or 'miles').

        Returns:
            EmissionResult with scope based on vehicle type.
        """
        self._validate_positive(distance, "distance")
        if passengers < 1:
            passengers = 1

        # Convert miles to km if needed
        distance_km = distance
        if unit.lower() in ("miles", "mile", "mi"):
            distance_km = FactorLoader.convert_unit(distance, "miles_to_km")

        factor = self._loader.get_transport_factor(mode, vehicle_type)
        scope = self._loader.get_transport_scope(mode, vehicle_type)
        emissions_kg = distance_km * factor / passengers

        label = vehicle_type or mode
        return EmissionResult(
            activity_type="transport",
            activity_amount=distance,
            activity_unit=unit,
            emissions_kg_co2e=emissions_kg,
            emissions_tonnes_co2e=emissions_kg / 1000,
            scope=scope,
            factor_used=factor,
            factor_source=f"UK DEFRA 2024 - {label}",
            calculation_details=(
                f"{distance:,.0f} {unit} by {label} × {factor} kg CO2e/km"
                + (f" ÷ {passengers} passengers" if passengers > 1 else "")
                + f" = {emissions_kg:,.2f} kg CO2e"
            ),
        )

    def calculate_flight(
        self,
        distance_km: Optional[float] = None,
        flight_type: str = "short_haul",
        flight_class: str = "economy",
        return_trip: bool = False,
        passengers: int = 1,
    ) -> EmissionResult:
        """Calculate emissions from flights.

        Args:
            distance_km: Actual flight distance in km. If None, uses average for flight_type.
            flight_type: Flight category ('domestic', 'short_haul', 'long_haul').
            flight_class: Cabin class ('economy', 'premium_economy', 'business', 'first').
            return_trip: If True, doubles the emissions.
            passengers: Number of passengers.

        Returns:
            EmissionResult with Scope 3 classification.
        """
        if distance_km is not None:
            self._validate_positive(distance_km, "flight distance")

        if distance_km is None:
            distance_km = self._loader.get_flight_average_distance(flight_type)

        factor = self._loader.get_transport_factor("flights", flight_type)
        multiplier = self._loader.get_flight_class_multiplier(flight_class)

        total_distance = distance_km * (2 if return_trip else 1)
        emissions_kg = total_distance * factor * multiplier * passengers

        return EmissionResult(
            activity_type="flight",
            activity_amount=total_distance,
            activity_unit="passenger-km",
            emissions_kg_co2e=emissions_kg,
            emissions_tonnes_co2e=emissions_kg / 1000,
            scope=3,
            factor_used=factor,
            factor_source=f"UK DEFRA 2024 - {flight_type} ({flight_class})",
            calculation_details=(
                f"{total_distance:,.0f} km ({flight_type}{'—return' if return_trip else ''}) "
                f"× {factor} kg CO2e/pkm × {multiplier}x ({flight_class})"
                + (f" × {passengers} pax" if passengers > 1 else "")
                + f" = {emissions_kg:,.2f} kg CO2e"
            ),
        )

    def calculate_waste(
        self,
        tonnes: float,
        disposal_method: str,
        material: Optional[str] = None,
    ) -> EmissionResult:
        """Calculate emissions from waste disposal.

        Args:
            tonnes: Weight of waste in tonnes.
            disposal_method: Disposal method (landfill_mixed, recycling_average, etc.).
            material: Optional specific material for recycling calculations.

        Returns:
            EmissionResult with Scope 3 classification.
        """
        self._validate_positive(tonnes, "waste tonnes")

        factor = self._loader.get_waste_factor(disposal_method, material)
        emissions_kg = tonnes * factor

        label = f"{material} recycling" if material else disposal_method
        return EmissionResult(
            activity_type="waste",
            activity_amount=tonnes,
            activity_unit="tonnes",
            emissions_kg_co2e=emissions_kg,
            emissions_tonnes_co2e=emissions_kg / 1000,
            scope=3,
            factor_used=factor,
            factor_source=f"UK DEFRA 2024 - {label}",
            calculation_details=(
                f"{tonnes:,.2f} tonnes ({label}) × {factor} kg CO2e/tonne = {emissions_kg:,.2f} kg CO2e"
            ),
        )

    def calculate_water(
        self,
        cubic_metres: float,
        include_treatment: bool = True,
    ) -> EmissionResult:
        """Calculate emissions from water consumption.

        Args:
            cubic_metres: Water volume in cubic metres.
            include_treatment: Whether to include treatment emissions.

        Returns:
            EmissionResult with Scope 3 classification.
        """
        self._validate_positive(cubic_metres, "water cubic metres")

        water_type = "supply_and_treatment" if include_treatment else "supply"
        factor = self._loader.get_water_factor(water_type)
        emissions_kg = cubic_metres * factor

        return EmissionResult(
            activity_type="water",
            activity_amount=cubic_metres,
            activity_unit="cubic metres",
            emissions_kg_co2e=emissions_kg,
            emissions_tonnes_co2e=emissions_kg / 1000,
            scope=3,
            factor_used=factor,
            factor_source=f"UK DEFRA 2024 - water {water_type}",
            calculation_details=(
                f"{cubic_metres:,.2f} m³ × {factor} kg CO2e/m³ ({water_type}) = {emissions_kg:,.2f} kg CO2e"
            ),
        )

    def calculate_single(self, activity: ActivityInput) -> EmissionResult:
        """Calculate emissions for a single activity input.

        Routes to the appropriate calculation method based on category.
        """
        cat = activity.category.strip().lower()

        if cat in ("electricity", "electric", "power", "grid"):
            return self.calculate_electricity(
                kwh=activity.amount,
                country=activity.country or "world_average",
            )
        elif cat in ("fuel", "fuels", "combustion", "gas", "heating"):
            return self.calculate_fuel(
                amount=activity.amount,
                fuel_type=activity.sub_category or "natural_gas",
                unit=activity.unit or "litres",
            )
        elif cat in ("transport", "travel", "vehicle", "road"):
            return self.calculate_transport(
                distance=activity.amount,
                mode="road",
                vehicle_type=activity.sub_category,
                unit=activity.unit or "km",
            )
        elif cat in ("flight", "flights", "air", "aviation", "air_travel"):
            return self.calculate_flight(
                distance_km=activity.amount if activity.unit in ("km", "kilometres", "kilometers") else None,
                flight_type=activity.sub_category or "short_haul",
                flight_class=activity.flight_class or "economy",
                return_trip=activity.return_trip,
            )
        elif cat in ("waste", "disposal", "rubbish"):
            return self.calculate_waste(
                tonnes=activity.amount,
                disposal_method=activity.sub_category or "landfill_mixed",
                material=None,
            )
        elif cat in ("water", "water_supply"):
            include_treatment = activity.sub_category not in ("supply_only", "supply")
            return self.calculate_water(
                cubic_metres=activity.amount,
                include_treatment=include_treatment,
            )
        else:
            raise ValueError(
                f"Unknown activity category: '{activity.category}'. "
                f"Supported: electricity, fuel, transport, flight, waste, water"
            )

    def calculate_total(self, activities: List[ActivityInput]) -> TotalEmissions:
        """Calculate total emissions for a list of activities.

        Returns aggregate results with scope and category breakdowns.
        """
        results: List[EmissionResult] = []
        warnings: List[str] = []

        for i, activity in enumerate(activities):
            try:
                result = self.calculate_single(activity)
                results.append(result)
            except (ValueError, FactorNotFoundError) as e:
                warnings.append(f"Row {i + 1}: {e}")

        total_kg = sum(r.emissions_kg_co2e for r in results)

        by_scope = {"scope_1": 0.0, "scope_2": 0.0, "scope_3": 0.0}
        for r in results:
            by_scope[f"scope_{r.scope}"] += r.emissions_kg_co2e

        by_category: Dict[str, float] = {}
        for r in results:
            by_category[r.activity_type] = by_category.get(r.activity_type, 0.0) + r.emissions_kg_co2e

        return TotalEmissions(
            total_kg_co2e=total_kg,
            total_tonnes_co2e=total_kg / 1000,
            by_scope=by_scope,
            by_category=by_category,
            breakdown=results,
            activity_count=len(results),
            warnings=warnings,
        )

    @staticmethod
    def _validate_positive(value: float, label: str) -> None:
        """Validate that a value is positive."""
        if value < 0:
            raise ValueError(f"{label} cannot be negative (got {value}).")
        if value > 1_000_000_000:
            # Warn but don't reject
            pass
