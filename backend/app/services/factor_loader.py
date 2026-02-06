"""Emission factor loader service for Carbon Compass.

Loads and queries conversion factor databases from UK DEFRA 2024 and IEA sources.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


# Unit conversion constants
CONVERSIONS = {
    "km_to_miles": 0.621371,
    "miles_to_km": 1.60934,
    "litres_to_gallons": 0.264172,
    "gallons_to_litres": 3.78541,
    "kg_to_tonnes": 0.001,
    "tonnes_to_kg": 1000,
    "cubic_metres_to_litres": 1000,
    "litres_to_cubic_metres": 0.001,
    "kwh_to_mwh": 0.001,
    "mwh_to_kwh": 1000,
}


class FactorNotFoundError(Exception):
    """Raised when a requested emission factor cannot be found."""
    pass


class FactorLoader:
    """Loads and queries emission factor databases.

    Loads JSON factor files from the data directory at initialization
    and provides typed accessor methods for each emission category.
    """

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent / "data" / "emission_factors"
        self._data_dir = data_dir
        self._factors: Dict[str, Any] = {}
        self.load_all_factors()

    def load_all_factors(self) -> None:
        """Load all emission factor JSON files from the data directory."""
        factor_files = ["electricity", "fuels", "transport", "waste", "water"]
        for name in factor_files:
            file_path = self._data_dir / f"{name}.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    self._factors[name] = json.load(f)
            else:
                print(f"Warning: Factor file not found: {file_path}")
                self._factors[name] = {}

    # ── Electricity ──────────────────────────────────────────────

    def get_electricity_factor(self, country: str) -> float:
        """Get grid electricity emission factor for a country.

        Args:
            country: Country name or key (e.g. 'united_kingdom', 'UK', 'United Kingdom')

        Returns:
            Emission factor in kg CO2e per kWh.

        Raises:
            FactorNotFoundError: If country is not found.
        """
        data = self._factors.get("electricity", {})
        factors = data.get("factors", {})

        # Normalise the key
        key = self._normalise_country_key(country)

        if key in factors:
            return factors[key]["value"]

        # Fallback to world average
        if "world_average" in factors:
            return factors["world_average"]["value"]

        raise FactorNotFoundError(f"No electricity factor found for country: {country}")

    def list_available_countries(self) -> List[Dict[str, str]]:
        """List all countries with available electricity factors."""
        data = self._factors.get("electricity", {})
        factors = data.get("factors", {})
        return [
            {"key": key, "name": info.get("name", key), "value": info["value"]}
            for key, info in factors.items()
        ]

    # ── Fuels ────────────────────────────────────────────────────

    def get_fuel_factor(self, fuel_type: str, unit: str = "litres") -> float:
        """Get emission factor for a fuel type in a given unit.

        Args:
            fuel_type: Fuel key (e.g. 'diesel', 'petrol', 'natural_gas')
            unit: Unit of measurement (e.g. 'litres', 'gallons', 'kg', 'kwh')

        Returns:
            Emission factor in kg CO2e per unit.

        Raises:
            FactorNotFoundError: If fuel type or unit is not found.
        """
        data = self._factors.get("fuels", {})
        fuels = data.get("fuels", {})

        key = self._normalise_key(fuel_type)
        if key not in fuels:
            raise FactorNotFoundError(
                f"Unknown fuel type: {fuel_type}. Available: {list(fuels.keys())}"
            )

        fuel = fuels[key]
        unit_key = self._normalise_unit(unit)

        if unit_key not in fuel["factors"]:
            raise FactorNotFoundError(
                f"Unit '{unit}' not available for {fuel_type}. "
                f"Available: {list(fuel['factors'].keys())}"
            )

        return fuel["factors"][unit_key]

    def get_fuel_scope(self, fuel_type: str) -> int:
        """Get the emission scope for a fuel type."""
        data = self._factors.get("fuels", {})
        fuels = data.get("fuels", {})
        key = self._normalise_key(fuel_type)
        if key in fuels:
            return fuels[key].get("scope", 1)
        return 1

    def list_available_fuels(self) -> List[Dict[str, Any]]:
        """List all available fuel types with their units."""
        data = self._factors.get("fuels", {})
        fuels = data.get("fuels", {})
        return [
            {
                "key": key,
                "name": info.get("name", key),
                "available_units": list(info.get("factors", {}).keys()),
                "default_unit": info.get("default_unit", "litres"),
            }
            for key, info in fuels.items()
        ]

    # ── Transport ────────────────────────────────────────────────

    def get_transport_factor(self, mode: str, vehicle_type: Optional[str] = None) -> float:
        """Get transport emission factor.

        Args:
            mode: Transport mode ('road', 'rail', 'shipping')
            vehicle_type: Specific vehicle (e.g. 'medium_petrol_car', 'national_rail')

        Returns:
            Emission factor in kg CO2e per km (or per passenger-km / tonne-km).

        Raises:
            FactorNotFoundError: If mode or vehicle type is not found.
        """
        data = self._factors.get("transport", {})

        mode_key = self._normalise_key(mode)

        if mode_key == "road" or mode_key in ("car", "van", "hgv", "bus", "taxi", "motorcycle"):
            return self._get_road_factor(data, vehicle_type or mode_key)
        elif mode_key in ("flight", "flights", "air"):
            return self._get_flight_factor(data, vehicle_type)
        elif mode_key == "rail":
            return self._get_rail_factor(data, vehicle_type)
        elif mode_key == "shipping":
            return self._get_shipping_factor(data, vehicle_type)
        else:
            raise FactorNotFoundError(
                f"Unknown transport mode: {mode}. Available: road, flights, rail, shipping"
            )

    def get_transport_scope(self, mode: str, vehicle_type: Optional[str] = None) -> int:
        """Get the scope for a transport type."""
        data = self._factors.get("transport", {})
        mode_key = self._normalise_key(mode)

        if mode_key == "road" or mode_key in ("car", "van", "hgv", "bus", "taxi", "motorcycle"):
            vehicles = data.get("road", {}).get("vehicles", {})
            vkey = self._normalise_key(vehicle_type) if vehicle_type else "average_car"
            if vkey in vehicles:
                return vehicles[vkey].get("scope", 3)
        return 3

    def get_flight_class_multiplier(self, flight_class: str = "economy") -> float:
        """Get the class multiplier for flights."""
        data = self._factors.get("transport", {})
        multipliers = data.get("flights", {}).get("class_multipliers", {})
        key = self._normalise_key(flight_class)
        return multipliers.get(key, 1.0)

    def get_flight_average_distance(self, flight_type: str) -> float:
        """Get average distance for a flight type in km."""
        data = self._factors.get("transport", {})
        distances = data.get("flights", {}).get("average_distances_km", {})
        key = self._normalise_key(flight_type)
        if key in distances:
            return distances[key]
        return 1500  # Default to short-haul

    def list_available_transport(self) -> Dict[str, List[Dict[str, Any]]]:
        """List all available transport types."""
        data = self._factors.get("transport", {})
        result: Dict[str, List[Dict[str, Any]]] = {}

        for mode in ["road", "rail", "shipping"]:
            section = data.get(mode, {})
            items_key = "vehicles" if mode == "road" else "types"
            items = section.get(items_key, {})
            result[mode] = [
                {"key": key, "name": info.get("name", key), "value": info["value"]}
                for key, info in items.items()
            ]

        flights = data.get("flights", {})
        result["flights"] = [
            {"key": key, "name": info.get("name", key), "value": info["value"]}
            for key, info in flights.get("types", {}).items()
        ]

        return result

    # ── Waste ────────────────────────────────────────────────────

    def get_waste_factor(self, disposal_method: str, material: Optional[str] = None) -> float:
        """Get waste disposal emission factor.

        Args:
            disposal_method: Method (e.g. 'landfill_mixed', 'recycling_average', 'composting')
            material: Optional specific material for recycling (e.g. 'paper', 'aluminium')

        Returns:
            Emission factor in kg CO2e per tonne. Negative values = avoided emissions.

        Raises:
            FactorNotFoundError: If disposal method or material is not found.
        """
        data = self._factors.get("waste", {})

        # If a specific material is given and method is recycling, use material factors
        if material:
            materials = data.get("material_recycling", {}).get("materials", {})
            mat_key = self._normalise_key(material)
            if mat_key in materials:
                return materials[mat_key]["value"]
            raise FactorNotFoundError(
                f"Unknown recycling material: {material}. "
                f"Available: {list(materials.keys())}"
            )

        methods = data.get("disposal_methods", {}).get("methods", {})
        method_key = self._normalise_key(disposal_method)
        if method_key in methods:
            return methods[method_key]["value"]

        raise FactorNotFoundError(
            f"Unknown disposal method: {disposal_method}. "
            f"Available: {list(methods.keys())}"
        )

    def list_available_waste_methods(self) -> List[Dict[str, Any]]:
        """List all available waste disposal methods."""
        data = self._factors.get("waste", {})
        methods = data.get("disposal_methods", {}).get("methods", {})
        materials = data.get("material_recycling", {}).get("materials", {})
        return {
            "disposal_methods": [
                {"key": key, "name": info.get("name", key), "value": info["value"]}
                for key, info in methods.items()
            ],
            "recycling_materials": [
                {"key": key, "name": info.get("name", key), "value": info["value"]}
                for key, info in materials.items()
            ],
        }

    # ── Water ────────────────────────────────────────────────────

    def get_water_factor(self, water_type: str = "supply_and_treatment") -> float:
        """Get water emission factor.

        Args:
            water_type: Type ('supply', 'treatment', or 'supply_and_treatment')

        Returns:
            Emission factor in kg CO2e per cubic metre.

        Raises:
            FactorNotFoundError: If water type is not found.
        """
        data = self._factors.get("water", {})
        factors = data.get("factors", {})
        key = self._normalise_key(water_type)

        if key in factors:
            return factors[key]["value"]

        raise FactorNotFoundError(
            f"Unknown water type: {water_type}. Available: {list(factors.keys())}"
        )

    # ── Unit Conversions ─────────────────────────────────────────

    @staticmethod
    def convert_unit(value: float, conversion: str) -> float:
        """Convert between units.

        Args:
            value: The value to convert.
            conversion: Conversion key (e.g. 'km_to_miles', 'litres_to_gallons').

        Returns:
            The converted value.

        Raises:
            ValueError: If the conversion is not known.
        """
        if conversion not in CONVERSIONS:
            raise ValueError(
                f"Unknown conversion: {conversion}. Available: {list(CONVERSIONS.keys())}"
            )
        return value * CONVERSIONS[conversion]

    # ── Private helpers ──────────────────────────────────────────

    def _get_road_factor(self, data: Dict, vehicle_type: str) -> float:
        vehicles = data.get("road", {}).get("vehicles", {})
        key = self._normalise_key(vehicle_type)
        if key in vehicles:
            return vehicles[key]["value"]
        # Try to find a partial match
        for vkey, info in vehicles.items():
            if key in vkey or vkey in key:
                return info["value"]
        if "average_car" in vehicles:
            return vehicles["average_car"]["value"]
        raise FactorNotFoundError(f"Unknown vehicle type: {vehicle_type}")

    def _get_flight_factor(self, data: Dict, flight_type: Optional[str]) -> float:
        flights = data.get("flights", {}).get("types", {})
        if not flight_type:
            return flights.get("short_haul", {}).get("value", 0.151)
        key = self._normalise_key(flight_type)
        if key in flights:
            return flights[key]["value"]
        raise FactorNotFoundError(f"Unknown flight type: {flight_type}")

    def _get_rail_factor(self, data: Dict, rail_type: Optional[str]) -> float:
        types = data.get("rail", {}).get("types", {})
        if not rail_type:
            return types.get("national_rail", {}).get("value", 0.035)
        key = self._normalise_key(rail_type)
        if key in types:
            return types[key]["value"]
        raise FactorNotFoundError(f"Unknown rail type: {rail_type}")

    def _get_shipping_factor(self, data: Dict, ship_type: Optional[str]) -> float:
        types = data.get("shipping", {}).get("types", {})
        if not ship_type:
            return types.get("container_ship", {}).get("value", 0.016)
        key = self._normalise_key(ship_type)
        if key in types:
            return types[key]["value"]
        raise FactorNotFoundError(f"Unknown shipping type: {ship_type}")

    @staticmethod
    def _normalise_key(value: str) -> str:
        """Normalise a string to a snake_case key."""
        return value.strip().lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")

    @staticmethod
    def _normalise_country_key(country: str) -> str:
        """Normalise a country name to match keys in the electricity factors."""
        key = country.strip().lower().replace(" ", "_").replace("-", "_")
        # Common aliases
        aliases = {
            "uk": "united_kingdom",
            "gb": "united_kingdom",
            "great_britain": "united_kingdom",
            "us": "united_states",
            "usa": "united_states",
            "america": "united_states",
            "emirates": "uae",
            "united_arab_emirates": "uae",
            "korea": "south_korea",
            "republic_of_korea": "south_korea",
        }
        return aliases.get(key, key)

    @staticmethod
    def _normalise_unit(unit: str) -> str:
        """Normalise unit strings."""
        key = unit.strip().lower().replace(" ", "_")
        aliases = {
            "l": "litres",
            "litre": "litres",
            "liter": "litres",
            "liters": "litres",
            "gal": "gallons",
            "gallon": "gallons",
            "m3": "cubic_metres",
            "m³": "cubic_metres",
            "cubic_meters": "cubic_metres",
            "cubic_meter": "cubic_metres",
            "cubic_metre": "cubic_metres",
            "therm": "therms",
            "kilogram": "kg",
            "kilograms": "kg",
            "tonne": "tonnes",
            "ton": "tonnes",
            "tons": "tonnes",
            "kilowatt_hour": "kwh",
            "kilowatt_hours": "kwh",
        }
        return aliases.get(key, key)
