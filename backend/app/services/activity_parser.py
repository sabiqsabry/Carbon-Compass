"""Activity data parser for CSV and Excel files.

Parses bulk activity data from uploaded files and converts them
to ActivityInput objects for emissions calculation.
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd

from .emissions_calculator import ActivityInput


@dataclass
class ValidationResult:
    """Result of validating parsed activities."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    valid_activities: List[ActivityInput]
    invalid_rows: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "valid_count": len(self.valid_activities),
            "invalid_count": len(self.invalid_rows),
            "invalid_rows": self.invalid_rows,
        }


# Column name mappings — maps common variations to canonical names
COLUMN_ALIASES: Dict[str, List[str]] = {
    "category": ["category", "type", "emission_type", "emission type", "activity_type", "activity type", "source_type"],
    "sub_category": ["sub_category", "sub-category", "subcategory", "activity", "source", "fuel_type", "fuel type", "vehicle_type", "vehicle type", "sub category"],
    "description": ["description", "desc", "details", "notes", "name", "label"],
    "amount": ["amount", "quantity", "value", "consumption", "usage", "volume", "distance"],
    "unit": ["unit", "units", "uom", "unit_of_measure", "measure", "unit of measure"],
    "country": ["country", "region", "location", "country_code", "country code", "grid"],
    "date": ["date", "period", "month", "year", "reporting_period", "reporting period", "time"],
}

# Category normalisation
CATEGORY_ALIASES: Dict[str, str] = {
    "electric": "electricity",
    "electricity": "electricity",
    "power": "electricity",
    "grid": "electricity",
    "energy": "electricity",
    "fuel": "fuel",
    "fuels": "fuel",
    "combustion": "fuel",
    "gas": "fuel",
    "natural gas": "fuel",
    "heating": "fuel",
    "transport": "transport",
    "transportation": "transport",
    "travel": "transport",
    "vehicle": "transport",
    "road": "transport",
    "car": "transport",
    "flight": "flight",
    "flights": "flight",
    "air": "flight",
    "air travel": "flight",
    "aviation": "flight",
    "waste": "waste",
    "disposal": "waste",
    "rubbish": "waste",
    "refuse": "waste",
    "water": "water",
    "water supply": "water",
    "water treatment": "water",
}

# Unit normalisation
UNIT_ALIASES: Dict[str, str] = {
    "kwh": "kWh",
    "kilowatt hours": "kWh",
    "kilowatt-hours": "kWh",
    "mwh": "MWh",
    "l": "litres",
    "litre": "litres",
    "liter": "litres",
    "liters": "litres",
    "litres": "litres",
    "gal": "gallons",
    "gallon": "gallons",
    "gallons": "gallons",
    "m3": "cubic_metres",
    "m³": "cubic_metres",
    "cubic meters": "cubic_metres",
    "cubic metres": "cubic_metres",
    "km": "km",
    "kilometres": "km",
    "kilometers": "km",
    "mi": "miles",
    "mile": "miles",
    "miles": "miles",
    "kg": "kg",
    "kilograms": "kg",
    "t": "tonnes",
    "tonne": "tonnes",
    "tonnes": "tonnes",
    "ton": "tonnes",
    "tons": "tonnes",
    "trips": "trips",
    "trip": "trips",
    "therms": "therms",
    "therm": "therms",
}


class ActivityParser:
    """Parses activity data from CSV and Excel files.

    Supports flexible column mapping with auto-detection of common
    column name variations.
    """

    def parse_file(
        self,
        file_path: str,
        column_mapping: Optional[Dict[str, str]] = None,
    ) -> List[ActivityInput]:
        """Parse activity data from a file path.

        Args:
            file_path: Path to CSV or Excel file.
            column_mapping: Optional manual column mapping override.

        Returns:
            List of parsed ActivityInput objects.
        """
        if file_path.endswith(".csv"):
            with open(file_path, "rb") as f:
                return self.parse_csv(f.read(), column_mapping)
        elif file_path.endswith((".xlsx", ".xls")):
            with open(file_path, "rb") as f:
                return self.parse_excel(f.read(), column_mapping=column_mapping)
        else:
            raise ValueError(f"Unsupported file format: {file_path}. Use .csv, .xlsx, or .xls")

    def parse_csv(
        self,
        file_content: bytes,
        column_mapping: Optional[Dict[str, str]] = None,
    ) -> List[ActivityInput]:
        """Parse activity data from CSV content.

        Args:
            file_content: Raw CSV file bytes.
            column_mapping: Optional manual column mapping.

        Returns:
            List of parsed ActivityInput objects.
        """
        df = pd.read_csv(io.BytesIO(file_content))
        return self._parse_dataframe(df, column_mapping)

    def parse_excel(
        self,
        file_content: bytes,
        sheet_name: Optional[str] = None,
        column_mapping: Optional[Dict[str, str]] = None,
    ) -> List[ActivityInput]:
        """Parse activity data from Excel content.

        Args:
            file_content: Raw Excel file bytes.
            sheet_name: Optional sheet name to read.
            column_mapping: Optional manual column mapping.

        Returns:
            List of parsed ActivityInput objects.
        """
        kwargs: Dict[str, Any] = {}
        if sheet_name:
            kwargs["sheet_name"] = sheet_name

        df = pd.read_excel(io.BytesIO(file_content), **kwargs)
        return self._parse_dataframe(df, column_mapping)

    def validate_activities(
        self,
        activities: List[ActivityInput],
    ) -> ValidationResult:
        """Validate a list of parsed activities.

        Checks for missing fields, invalid units, etc.

        Returns:
            ValidationResult with valid/invalid activities separated.
        """
        valid: List[ActivityInput] = []
        invalid: List[Dict[str, Any]] = []
        errors: List[str] = []
        warnings: List[str] = []

        for i, act in enumerate(activities):
            row_num = i + 1
            row_errors: List[str] = []

            # Check required fields
            if not act.category:
                row_errors.append("Missing category")
            elif act.category not in ("electricity", "fuel", "transport", "flight", "waste", "water"):
                row_errors.append(f"Unknown category: '{act.category}'")

            if act.amount <= 0:
                row_errors.append(f"Invalid amount: {act.amount}")

            if not act.unit and act.category != "electricity":
                row_errors.append("Missing unit")

            # Category-specific validation
            if act.category == "electricity" and not act.country:
                warnings.append(f"Row {row_num}: No country specified for electricity, will use world average")

            if row_errors:
                errors.append(f"Row {row_num}: {'; '.join(row_errors)}")
                invalid.append({
                    "row": row_num,
                    "errors": row_errors,
                    "data": act.raw_row or {},
                })
            else:
                valid.append(act)

        return ValidationResult(
            valid=len(invalid) == 0,
            errors=errors,
            warnings=warnings,
            valid_activities=valid,
            invalid_rows=invalid,
        )

    def detect_columns(self, file_content: bytes, file_type: str = "csv") -> Dict[str, Optional[str]]:
        """Detect column mappings from file headers.

        Args:
            file_content: Raw file bytes.
            file_type: Either 'csv' or 'excel'.

        Returns:
            Dict mapping canonical field names to detected column names.
        """
        if file_type == "csv":
            df = pd.read_csv(io.BytesIO(file_content), nrows=0)
        else:
            df = pd.read_excel(io.BytesIO(file_content), nrows=0)

        return self._auto_detect_columns(df.columns.tolist())

    def get_file_preview(
        self,
        file_content: bytes,
        file_type: str = "csv",
        max_rows: int = 5,
    ) -> Dict[str, Any]:
        """Get a preview of the uploaded file.

        Returns columns and first N rows for user review.
        """
        if file_type == "csv":
            df = pd.read_csv(io.BytesIO(file_content), nrows=max_rows)
        else:
            df = pd.read_excel(io.BytesIO(file_content), nrows=max_rows)

        return {
            "columns": df.columns.tolist(),
            "rows": df.fillna("").to_dict(orient="records"),
            "total_columns": len(df.columns),
            "detected_mapping": self._auto_detect_columns(df.columns.tolist()),
        }

    # ── Private methods ──────────────────────────────────────────

    def _parse_dataframe(
        self,
        df: pd.DataFrame,
        column_mapping: Optional[Dict[str, str]] = None,
    ) -> List[ActivityInput]:
        """Parse a DataFrame into ActivityInput objects."""
        # Clean up column names
        df.columns = [str(c).strip() for c in df.columns]

        # Drop fully empty rows
        df = df.dropna(how="all")

        # Determine column mapping
        if column_mapping:
            mapping = column_mapping
        else:
            mapping = self._auto_detect_columns(df.columns.tolist())

        activities: List[ActivityInput] = []

        for _, row in df.iterrows():
            try:
                raw = row.to_dict()

                # Extract fields using mapping
                category_raw = self._get_field(row, mapping.get("category"))
                if not category_raw:
                    continue  # Skip rows without a category

                category = self._normalise_category(str(category_raw))
                sub_category = self._get_field(row, mapping.get("sub_category"))
                description = self._get_field(row, mapping.get("description"))
                amount = self._parse_number(self._get_field(row, mapping.get("amount")))
                unit_raw = self._get_field(row, mapping.get("unit"))
                country = self._get_field(row, mapping.get("country"))
                date = self._get_field(row, mapping.get("date"))

                if amount is None or amount == 0:
                    continue  # Skip rows with no amount

                unit = self._normalise_unit(str(unit_raw)) if unit_raw else self._default_unit(category)

                activities.append(ActivityInput(
                    category=category,
                    sub_category=str(sub_category) if sub_category else None,
                    description=str(description) if description else None,
                    amount=amount,
                    unit=unit,
                    country=str(country) if country else None,
                    date=str(date) if date else None,
                    raw_row=raw,
                ))
            except Exception:
                continue  # Skip unparseable rows

        return activities

    def _auto_detect_columns(self, columns: List[str]) -> Dict[str, Optional[str]]:
        """Auto-detect column mapping based on common name variations."""
        mapping: Dict[str, Optional[str]] = {}
        lower_columns = {c.strip().lower().replace(" ", "_"): c for c in columns}

        for field_name, aliases in COLUMN_ALIASES.items():
            mapping[field_name] = None
            for alias in aliases:
                normalised = alias.strip().lower().replace(" ", "_")
                if normalised in lower_columns:
                    mapping[field_name] = lower_columns[normalised]
                    break
            # Partial match fallback
            if mapping[field_name] is None:
                for col_lower, col_original in lower_columns.items():
                    for alias in aliases:
                        if alias in col_lower or col_lower in alias:
                            mapping[field_name] = col_original
                            break
                    if mapping[field_name] is not None:
                        break

        return mapping

    @staticmethod
    def _get_field(row: pd.Series, column: Optional[str]) -> Any:
        """Safely get a field from a row."""
        if column is None:
            return None
        val = row.get(column)
        if pd.isna(val):
            return None
        return val

    @staticmethod
    def _parse_number(value: Any) -> Optional[float]:
        """Parse a numeric value, handling commas and strings."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        try:
            cleaned = str(value).strip().replace(",", "").replace(" ", "")
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _normalise_category(raw: str) -> str:
        """Normalise a category string to canonical form."""
        key = raw.strip().lower()
        return CATEGORY_ALIASES.get(key, key)

    @staticmethod
    def _normalise_unit(raw: str) -> str:
        """Normalise a unit string."""
        key = raw.strip().lower()
        return UNIT_ALIASES.get(key, raw.strip())

    @staticmethod
    def _default_unit(category: str) -> str:
        """Get a sensible default unit for a category."""
        defaults = {
            "electricity": "kWh",
            "fuel": "litres",
            "transport": "km",
            "flight": "trips",
            "waste": "tonnes",
            "water": "cubic_metres",
        }
        return defaults.get(category, "")
