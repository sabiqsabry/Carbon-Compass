# Carbon Compass — Structured Data Route Extension
## Emissions Calculator & Activity Data Analysis

---

## What You're Adding

An extension to Carbon Compass that allows users to:
- Input activity data (energy, fuel, travel, waste) and calculate emissions using official conversion factors
- Upload CSV/Excel files with bulk activity data
- Compare calculated emissions against what the NLP route extracted from reports
- Benchmark against industry averages
- Generate Scope 1, 2, 3 breakdowns automatically

---

## How It Connects to Your Existing NLP Route

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CARBON COMPASS                                │
├─────────────────────────────────┬───────────────────────────────────┤
│         NLP ROUTE               │      STRUCTURED DATA ROUTE        │
│   (What companies CLAIM)        │    (What the numbers SHOW)        │
├─────────────────────────────────┼───────────────────────────────────┤
│ • PDF report analysis           │ • Activity data input             │
│ • Metric extraction from text   │ • Emissions calculation           │
│ • Greenwashing detection        │ • Standard conversion factors     │
│ • Risk scoring                  │ • CSV/Excel bulk upload           │
├─────────────────────────────────┴───────────────────────────────────┤
│                      COMPARISON ENGINE                               │
│         Compare extracted claims vs calculated actuals               │
│              Flag discrepancies • Verify accuracy                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## New Project Structure (Additions Only)

```
carbon-compass/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── ... (existing)
│   │   │   ├── calculator.py        # NEW: Emissions calculator endpoints
│   │   │   └── verification.py      # NEW: Compare NLP vs calculated
│   │   ├── services/
│   │   │   ├── ... (existing)
│   │   │   ├── emissions_calculator.py   # NEW
│   │   │   ├── activity_parser.py        # NEW: CSV/Excel parsing
│   │   │   └── verification_engine.py    # NEW
│   │   └── data/
│   │       └── emission_factors/         # NEW: Conversion factor databases
│   │           ├── electricity.json
│   │           ├── fuels.json
│   │           ├── transport.json
│   │           ├── waste.json
│   │           └── water.json
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── ... (existing)
│   │   │   ├── CalculatorPage.tsx    # NEW
│   │   │   ├── BulkUploadPage.tsx    # NEW
│   │   │   └── VerificationPage.tsx  # NEW
│   │   ├── components/
│   │   │   ├── ... (existing)
│   │   │   ├── ActivityForm.tsx      # NEW
│   │   │   ├── EmissionsBreakdown.tsx # NEW
│   │   │   ├── ScopeChart.tsx        # NEW
│   │   │   └── DiscrepancyAlert.tsx  # NEW
```

---

## Phase 1: Emissions Factor Data Collection

Before coding, you need the conversion factor databases. Here's exactly what to collect and where to get it.

### Data Sources (All Free)

| Source | URL | What You Get |
|--------|-----|--------------|
| UK DEFRA | https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024 | Excel file with all conversion factors — this is your primary source |
| US EPA | https://www.epa.gov/climateleadership/ghg-emission-factors-hub | US-specific factors |
| IPCC | https://www.ipcc-nggip.iges.or.jp/EFDB/main.php | International default factors |
| IEA | https://www.iea.org/data-and-statistics/data-product/emissions-factors-2024 | Electricity grid factors by country |

### Primary Source: UK DEFRA 2024

Download the DEFRA Excel file — it contains everything you need in one place. You'll extract data from these sheets:

1. **Fuels** — Petrol, diesel, natural gas, LPG, coal, etc.
2. **Electricity** — Grid factors by country
3. **Transport** — Cars, vans, HGVs, flights, rail, shipping
4. **Waste** — Landfill, recycling, composting, incineration
5. **Water** — Supply and treatment
6. **Materials** — Embodied carbon in materials (optional for v1)

---

## Phase 2: Building the Structured Data Backend

### CURSOR PROMPT 21: Emissions Factor Data Setup

```
Create the emissions factor data structure and loader for Carbon Compass.

Context: This extends Carbon Compass to add a Structured Data route. We need to store conversion factors from UK DEFRA and other sources.

Files to create:
- backend/app/data/emission_factors/electricity.json
- backend/app/data/emission_factors/fuels.json
- backend/app/data/emission_factors/transport.json
- backend/app/data/emission_factors/waste.json
- backend/app/data/emission_factors/water.json
- backend/app/services/factor_loader.py

Requirements:

1. electricity.json - Grid emission factors by country (kg CO2e per kWh):
   Include at least these countries with 2024 factors:
   - Sri Lanka: 0.731
   - United Kingdom: 0.207
   - United States: 0.417
   - UAE: 0.442
   - Saudi Arabia: 0.525
   - India: 0.708
   - China: 0.555
   - Germany: 0.364
   - France: 0.052
   - Australia: 0.68
   - Singapore: 0.408
   - Japan: 0.471
   - South Korea: 0.459
   - Canada: 0.120
   - Brazil: 0.074
   
   Structure:
   {
     "unit": "kg CO2e per kWh",
     "source": "IEA/DEFRA 2024",
     "factors": {
       "sri_lanka": { "value": 0.731, "year": 2024 },
       ...
     }
   }

2. fuels.json - Fuel combustion factors (kg CO2e per unit):
   Include:
   - Petrol/Gasoline: 2.31 kg CO2e per litre
   - Diesel: 2.68 kg CO2e per litre
   - Natural Gas: 2.02 kg CO2e per cubic meter
   - LPG: 1.56 kg CO2e per litre
   - Coal (industrial): 2.42 kg CO2e per kg
   - Heating Oil: 2.54 kg CO2e per litre
   - Aviation Fuel: 2.55 kg CO2e per litre
   
   Structure with unit conversions available (litres, gallons, kg, therms, etc.)

3. transport.json - Transport emission factors:
   
   Road (kg CO2e per km):
   - Small petrol car: 0.14
   - Medium petrol car: 0.17
   - Large petrol car: 0.21
   - Small diesel car: 0.12
   - Medium diesel car: 0.16
   - Large diesel car: 0.19
   - Electric car (average grid): 0.05
   - Motorcycle: 0.08
   - Van: 0.24
   - HGV (rigid): 0.48
   - HGV (articulated): 0.93
   
   Flights (kg CO2e per passenger-km, including radiative forcing):
   - Domestic: 0.246
   - Short-haul international: 0.151
   - Long-haul international: 0.195
   - Business class multiplier: 2.0
   - First class multiplier: 4.0
   
   Rail (kg CO2e per passenger-km):
   - National rail: 0.035
   - Light rail/metro: 0.029
   
   Shipping (kg CO2e per tonne-km):
   - Container ship: 0.016
   - Bulk carrier: 0.005

4. waste.json - Waste disposal factors (kg CO2e per tonne):
   - Landfill (mixed waste): 446
   - Landfill (food waste): 580
   - Incineration: 21
   - Recycling (average): -50 (negative = avoided emissions)
   - Composting: 10
   - Anaerobic digestion: -100
   
   By material (recycling savings):
   - Paper: -800
   - Plastic: -1400
   - Glass: -300
   - Aluminium: -9000
   - Steel: -1800

5. water.json - Water factors (kg CO2e per cubic meter):
   - Water supply: 0.149
   - Water treatment: 0.272
   - Total (supply + treatment): 0.421

6. factor_loader.py - Service to load and query factors:
   - FactorLoader class
   - load_all_factors() -> loads all JSON files at startup
   - get_electricity_factor(country: str) -> float
   - get_fuel_factor(fuel_type: str, unit: str) -> float
   - get_transport_factor(mode: str, vehicle_type: str) -> float
   - get_waste_factor(disposal_method: str, material: str = None) -> float
   - get_water_factor(type: str) -> float
   - list_available_countries() -> list
   - list_available_fuels() -> list
   - Unit conversion helpers (litres to gallons, km to miles, etc.)

Make the JSON files comprehensive but not overwhelming. Include source attribution and year for each factor. Handle missing factors gracefully with sensible defaults or errors.
```

---

### CURSOR PROMPT 22: Emissions Calculator Service

```
Create the core emissions calculator service for Carbon Compass.

File: backend/app/services/emissions_calculator.py

Context: This service uses the emission factors from factor_loader.py to calculate emissions from activity data.

Requirements:

1. Create an EmissionsCalculator class with methods for each emission category:

   calculate_electricity(
       kwh: float,
       country: str,
       renewable_percentage: float = 0
   ) -> EmissionResult
   
   calculate_fuel(
       amount: float,
       fuel_type: str,
       unit: str = "litres"
   ) -> EmissionResult
   
   calculate_transport(
       distance: float,
       mode: str,
       vehicle_type: str = None,
       passengers: int = 1,
       unit: str = "km"
   ) -> EmissionResult
   
   calculate_flight(
       origin: str,
       destination: str,
       flight_class: str = "economy",
       return_trip: bool = False
   ) -> EmissionResult
   # Use approximate distances: short-haul <3h, long-haul >6h
   
   calculate_waste(
       tonnes: float,
       disposal_method: str,
       material: str = None
   ) -> EmissionResult
   
   calculate_water(
       cubic_meters: float,
       include_treatment: bool = True
   ) -> EmissionResult

2. Create an EmissionResult dataclass:
   - activity_type: str
   - activity_amount: float
   - activity_unit: str
   - emissions_kg_co2e: float
   - emissions_tonnes_co2e: float
   - scope: int (1, 2, or 3)
   - factor_used: float
   - factor_source: str
   - calculation_details: str (human-readable breakdown)

3. Scope classification:
   - Scope 1 (Direct): Fuel combustion on-site, company vehicles
   - Scope 2 (Indirect - Energy): Purchased electricity, heat, steam
   - Scope 3 (Indirect - Value Chain): Business travel, waste, water, supply chain

4. Create a bulk calculation method:
   calculate_total(activities: List[ActivityInput]) -> TotalEmissions
   
   Where TotalEmissions includes:
   - total_kg_co2e: float
   - total_tonnes_co2e: float
   - by_scope: dict (scope 1, 2, 3 totals)
   - by_category: dict (electricity, fuel, transport, waste, water)
   - breakdown: List[EmissionResult]

5. Handle edge cases:
   - Unknown countries -> use world average
   - Invalid fuel types -> raise clear error
   - Negative values -> reject
   - Very large values -> warn but allow

Include proper type hints and docstrings.
```

---

### CURSOR PROMPT 23: Activity Data Parser (CSV/Excel)

```
Create a service to parse activity data from CSV and Excel files for Carbon Compass.

File: backend/app/services/activity_parser.py

Requirements:

1. Create an ActivityParser class that handles:
   - CSV files
   - Excel files (.xlsx, .xls)
   - Flexible column mapping

2. Expected input formats (should handle variations):

   Format A - Simple:
   | Category | Activity | Amount | Unit |
   |----------|----------|--------|------|
   | Electricity | Grid power | 50000 | kWh |
   | Fuel | Diesel | 10000 | litres |
   | Transport | Car travel | 25000 | km |

   Format B - Detailed:
   | Date | Category | Sub-category | Description | Amount | Unit | Country/Region |
   |------|----------|--------------|-------------|--------|------|----------------|
   | 2024-01 | Electricity | Grid | Office HQ | 5000 | kWh | Sri Lanka |
   | 2024-01 | Transport | Flight | Colombo-Dubai | 1 | trip | - |

3. Column mapping logic:
   - Auto-detect common column names (case-insensitive):
     - Category/Type/Emission Type
     - Activity/Sub-category/Source
     - Amount/Quantity/Value
     - Unit/Units/UOM
     - Country/Region/Location
     - Date/Period/Month
   - Allow manual column mapping override

4. Parsing methods:
   
   parse_file(
       file_path: str,
       column_mapping: dict = None
   ) -> List[ActivityInput]
   
   parse_csv(
       file_content: bytes,
       column_mapping: dict = None
   ) -> List[ActivityInput]
   
   parse_excel(
       file_content: bytes,
       sheet_name: str = None,
       column_mapping: dict = None
   ) -> List[ActivityInput]
   
   validate_activities(
       activities: List[ActivityInput]
   ) -> ValidationResult
   # Check for missing fields, invalid units, etc.

5. Create ActivityInput dataclass:
   - category: str (electricity, fuel, transport, waste, water)
   - sub_category: str (optional - grid, diesel, flight, etc.)
   - description: str (optional)
   - amount: float
   - unit: str
   - country: str (optional, for electricity)
   - date: str (optional)
   - raw_row: dict (original data for debugging)

6. Create ValidationResult dataclass:
   - valid: bool
   - errors: List[str]
   - warnings: List[str]
   - valid_activities: List[ActivityInput]
   - invalid_rows: List[dict]

7. Handle common issues:
   - Skip empty rows
   - Handle numeric strings with commas (1,000 -> 1000)
   - Normalise units (Litres/liters/L -> litres)
   - Normalise categories (Electric/Electricity/Power -> electricity)
   - Flag rows with missing required fields

Use pandas for parsing. Include helpful error messages.
```

---

### CURSOR PROMPT 24: Verification Engine (Compare NLP vs Calculated)

```
Create a verification engine for Carbon Compass that compares NLP-extracted metrics against calculated emissions.

File: backend/app/services/verification_engine.py

Context: Carbon Compass has two routes:
1. NLP Route - extracts metrics from sustainability reports (what companies CLAIM)
2. Structured Data Route - calculates emissions from activity data (what numbers SHOW)

This service compares the two to find discrepancies.

Requirements:

1. Create a VerificationEngine class:

   compare(
       nlp_metrics: List[ExtractedMetric],  # From NLP route
       calculated_emissions: TotalEmissions  # From calculator
   ) -> VerificationResult

2. VerificationResult dataclass:
   - match_score: float (0-100, how well they align)
   - discrepancies: List[Discrepancy]
   - verified_metrics: List[VerifiedMetric]
   - summary: str
   - recommendations: List[str]

3. Discrepancy dataclass:
   - metric_type: str (e.g., "Scope 1 Emissions")
   - reported_value: float (from NLP)
   - reported_unit: str
   - calculated_value: float (from calculator)
   - calculated_unit: str
   - difference_absolute: float
   - difference_percentage: float
   - severity: str (minor/moderate/major)
   - possible_explanations: List[str]

4. Comparison logic:
   
   Match categories:
   - NLP "Scope 1 emissions" <-> Calculator Scope 1 total
   - NLP "Scope 2 emissions" <-> Calculator Scope 2 total
   - NLP "Scope 3 emissions" <-> Calculator Scope 3 total
   - NLP "Total emissions" <-> Calculator total
   - NLP "Electricity consumption" <-> Calculator electricity input (kWh)
   - NLP "Energy consumption" <-> Calculator fuel + electricity
   
   Tolerance thresholds:
   - Minor discrepancy: <10% difference
   - Moderate discrepancy: 10-25% difference
   - Major discrepancy: >25% difference

5. Possible explanations to suggest:
   - "Different reporting boundaries"
   - "Different methodology (location-based vs market-based)"
   - "Missing Scope 3 categories in calculation"
   - "Estimation vs actual data"
   - "Different reporting periods"
   - "Unit conversion differences"
   - "Potential data error in report"
   - "Potential calculation input error"

6. Generate recommendations:
   - If calculated > reported: "Reported emissions may be understated"
   - If calculated < reported: "Company may be over-reporting (conservative)"
   - If Scope 3 missing from calculation: "Add supply chain data for complete comparison"
   - If close match: "Reported figures align with calculated estimates"

7. Edge cases:
   - NLP couldn't extract a metric -> mark as "unverified"
   - No activity data for a scope -> mark as "not calculated"
   - Different units -> convert before comparing

Include confidence scores based on data completeness.
```

---

### CURSOR PROMPT 25: Calculator API Routes

```
Create API routes for the Structured Data route in Carbon Compass.

Files:
- backend/app/api/routes/calculator.py
- backend/app/api/routes/verification.py
- Update backend/app/models/schemas.py with new models

Requirements:

1. calculator.py routes:

   POST /api/v1/calculate/single
   - Calculate emissions for a single activity
   - Body: { category, sub_category, amount, unit, country? }
   - Returns: EmissionResult

   POST /api/v1/calculate/bulk
   - Calculate emissions for multiple activities
   - Body: { activities: [...] }
   - Returns: TotalEmissions with breakdown

   POST /api/v1/calculate/upload
   - Upload CSV/Excel file and calculate
   - Multipart form with file
   - Returns: TotalEmissions + parsing warnings

   GET /api/v1/calculate/factors
   - List all available emission factors
   - Query params: category (electricity, fuel, transport, waste, water)
   - Returns: Available factors with values

   GET /api/v1/calculate/countries
   - List countries with electricity factors
   - Returns: List of country codes and names

2. verification.py routes:

   POST /api/v1/verify/{report_filename}
   - Compare NLP analysis of a report against calculated emissions
   - Body: { activities: [...] } OR upload file
   - Returns: VerificationResult with discrepancies

   GET /api/v1/verify/{report_filename}/summary
   - Get a summary of verification status
   - Returns: Quick overview (match score, major discrepancies count)

3. Update schemas.py with:
   - ActivityInput (for request body)
   - EmissionResultResponse
   - TotalEmissionsResponse
   - VerificationResultResponse
   - DiscrepancyResponse
   - FactorListResponse

4. Update main.py to include the new routers

5. Error handling:
   - 400 for invalid input (unknown fuel type, negative values)
   - 404 for unknown countries (suggest alternatives)
   - 422 for unparseable files

Include OpenAPI descriptions for all endpoints.
```

---

## Phase 3: Building the Frontend Extensions

### CURSOR PROMPT 26: Calculator Page

```
Create the emissions calculator page for Carbon Compass.

Files:
- src/pages/CalculatorPage.tsx
- src/components/calculator/ActivityForm.tsx
- src/components/calculator/EmissionsResult.tsx
- src/components/calculator/ScopeBreakdown.tsx

Requirements:

1. CalculatorPage.tsx:
   - Header: "Emissions Calculator"
   - Subtitle: "Calculate your carbon footprint from activity data"
   - Two tabs: "Manual Entry" | "Bulk Upload"
   - Results section below

2. ActivityForm.tsx (Manual Entry):
   - Form to add activities one by one
   - Fields:
     - Category dropdown: Electricity, Fuel, Transport, Waste, Water
     - Sub-category dropdown (changes based on category):
       - Electricity: just country selector
       - Fuel: Petrol, Diesel, Natural Gas, LPG, etc.
       - Transport: Car, Van, Flight, Rail, etc.
       - Waste: Landfill, Recycling, Composting, etc.
       - Water: Supply, Treatment, Both
     - Amount: number input
     - Unit: dropdown (changes based on category)
     - Country: dropdown (for electricity)
   - "Add Activity" button -> adds to list below
   - List of added activities with remove button
   - "Calculate Total" button

3. EmissionsResult.tsx:
   - Display after calculation
   - Large total: "X.XX tonnes CO2e"
   - Equivalency: "Equivalent to X return flights London-New York"
   - Breakdown table: each activity with its emissions
   - Download as CSV button

4. ScopeBreakdown.tsx:
   - Pie or donut chart showing Scope 1, 2, 3 split
   - Use Recharts
   - Colors: Scope 1 (red), Scope 2 (yellow), Scope 3 (blue)
   - Legend with percentages
   - Click segment to see activities in that scope

Style to match existing Carbon Compass theme. Use emerald accents.
```

---

### CURSOR PROMPT 27: Bulk Upload Page

```
Create the bulk upload page for Carbon Compass emissions calculator.

Files:
- src/pages/BulkUploadPage.tsx
- src/components/calculator/FileUploader.tsx
- src/components/calculator/ColumnMapper.tsx
- src/components/calculator/ValidationErrors.tsx

Requirements:

1. BulkUploadPage.tsx:
   - Header: "Bulk Emissions Calculator"
   - Subtitle: "Upload your activity data as CSV or Excel"
   - Steps: 1. Upload → 2. Map Columns → 3. Review → 4. Calculate
   - Progress indicator showing current step

2. FileUploader.tsx:
   - Drag-and-drop zone for CSV/Excel
   - Accept: .csv, .xlsx, .xls
   - Max size: 10MB
   - Show file preview after upload (first 5 rows)
   - "Download Template" link for sample CSV format

3. ColumnMapper.tsx:
   - Show detected columns from uploaded file
   - Dropdowns to map each to required fields:
     - Category (required)
     - Amount (required)
     - Unit (required)
     - Sub-category (optional)
     - Country (optional)
     - Date (optional)
   - Auto-detect common column names
   - Preview how data will be interpreted

4. ValidationErrors.tsx:
   - Show any parsing errors or warnings
   - Table of problematic rows:
     - Row number
     - Issue description
     - Original data
   - Option to skip invalid rows and continue
   - "Fix and Re-upload" button

5. After successful calculation:
   - Show EmissionsResult and ScopeBreakdown (reuse from CalculatorPage)
   - Show how many rows processed
   - "Save Results" button

Provide a downloadable CSV template with example data:
Category,Sub-category,Amount,Unit,Country
Electricity,Grid,50000,kWh,Sri Lanka
Fuel,Diesel,5000,litres,
Transport,Flight (short-haul),10,trips,
Waste,Landfill,50,tonnes,
```

---

### CURSOR PROMPT 28: Verification Page

```
Create the verification page for Carbon Compass that compares NLP analysis against calculated emissions.

Files:
- src/pages/VerificationPage.tsx
- src/components/verification/ReportSelector.tsx
- src/components/verification/DiscrepancyList.tsx
- src/components/verification/MatchScoreGauge.tsx
- src/components/verification/ComparisonTable.tsx

Requirements:

1. VerificationPage.tsx:
   - Header: "Verify Report Claims"
   - Subtitle: "Compare what's reported vs. what the numbers show"
   - Two-column layout:
     - Left: Select report + enter activity data
     - Right: Verification results
   - This is a key differentiator feature - make it prominent

2. ReportSelector.tsx:
   - Dropdown to select from analysed reports
   - Shows report name and risk score badge
   - After selection, shows extracted metrics summary:
     - "Report claims: Scope 1: X tonnes, Scope 2: Y tonnes..."
   - "Select a different report" link

3. Activity data input:
   - Reuse ActivityForm from calculator
   - OR file upload option
   - "Verify Against Report" button

4. MatchScoreGauge.tsx:
   - Circular gauge showing match score (0-100%)
   - Color: green (>80%), yellow (50-80%), red (<50%)
   - Center text: "85% Match" or "Needs Review"
   - Below: interpretation text
     - "Reported figures closely align with calculated estimates"
     - "Significant discrepancies detected - review recommended"

5. DiscrepancyList.tsx:
   - List of discrepancies found
   - Each item shows:
     - Metric name (e.g., "Scope 1 Emissions")
     - Reported value: "12,500 tonnes"
     - Calculated value: "15,200 tonnes"
     - Difference: "+21.6% (2,700 tonnes)"
     - Severity badge (minor/moderate/major)
     - Expandable: possible explanations
   - Sort by severity (major first)

6. ComparisonTable.tsx:
   - Side-by-side table:
     | Metric | Reported | Calculated | Difference | Status |
   - Status icons: ✓ (match), ⚠ (minor), ✗ (major)
   - Rows for each scope and total
   - Footer row with overall assessment

7. Recommendations section:
   - List of actionable recommendations based on findings
   - E.g., "Add Scope 3 supply chain data for complete comparison"
   - E.g., "Reported Scope 1 is 21% lower than calculated - investigate"

Make this page feel like a forensic analysis tool. Professional, data-dense, but readable.
```

---

### CURSOR PROMPT 29: Update Navigation and Dashboard

```
Update Carbon Compass navigation and dashboard to include the new Structured Data route features.

Files to modify:
- src/components/Sidebar.tsx
- src/components/Header.tsx
- src/pages/DashboardPage.tsx
- src/App.tsx (routes)

Requirements:

1. Sidebar.tsx - Add new navigation items:
   
   Existing:
   - Dashboard
   - Upload
   - Reports
   - Compare
   
   Add new section "Calculate":
   - Calculator (icon: calculator)
   - Bulk Upload (icon: file-spreadsheet)
   - Verify Report (icon: check-circle or shield-check)
   
   Visual separator between Report Analysis and Calculate sections

2. App.tsx - Add new routes:
   - /calculator -> CalculatorPage
   - /calculator/bulk -> BulkUploadPage
   - /verify -> VerificationPage
   - /verify/:filename -> VerificationPage with pre-selected report

3. DashboardPage.tsx - Add new stats and quick actions:
   
   New stat cards:
   - "Calculations Made" (count of saved calculations)
   - "Verifications Run" (count of verification comparisons)
   
   Update QuickActions:
   - Add "Calculate Emissions" card -> /calculator
   - Add "Verify a Report" card -> /verify
   
   Add new section "How It Works":
   - Brief explanation of the two routes
   - "Analyse Reports" - extract metrics from PDFs
   - "Calculate Emissions" - compute from activity data
   - "Verify Claims" - compare the two

4. Header.tsx:
   - No changes needed, but ensure breadcrumbs work for new pages

Keep the design consistent with existing pages.
```

---

### CURSOR PROMPT 30: Update Database for Calculations

```
Add database models and persistence for the Structured Data route in Carbon Compass.

Files to modify:
- backend/app/models/orm_models.py
- backend/app/api/routes/calculator.py (add save functionality)

New tables to add:

1. Calculation:
   - id: UUID primary key
   - name: String (optional, user-provided name)
   - created_at: DateTime
   - total_emissions_kg: Float
   - scope_1_kg: Float
   - scope_2_kg: Float
   - scope_3_kg: Float
   - activity_count: Integer
   - source_file: String (nullable, if from upload)

2. CalculationActivity:
   - id: UUID primary key
   - calculation_id: FK to Calculation
   - category: String
   - sub_category: String (nullable)
   - description: String (nullable)
   - amount: Float
   - unit: String
   - country: String (nullable)
   - emissions_kg: Float
   - scope: Integer
   - factor_used: Float

3. Verification:
   - id: UUID primary key
   - report_id: FK to Report (from NLP route)
   - calculation_id: FK to Calculation
   - verified_at: DateTime
   - match_score: Float
   - discrepancy_count: Integer
   - summary: Text

4. VerificationDiscrepancy:
   - id: UUID primary key
   - verification_id: FK to Verification
   - metric_type: String
   - reported_value: Float
   - calculated_value: Float
   - difference_percentage: Float
   - severity: String

Update calculator.py routes:
- Add POST /api/v1/calculate/save to persist a calculation
- Add GET /api/v1/calculations to list saved calculations
- Add GET /api/v1/calculations/{id} to get a saved calculation

Update verification.py routes:
- Save verification results to database
- Add GET /api/v1/verifications to list past verifications

Add proper indexes and cascade deletes.
```

---

## Phase 4: Documentation Updates

### CURSOR PROMPT 31: Update README for Structured Data Route

```
Update the Carbon Compass README.md to include the Structured Data route.

Add/modify these sections:

1. Update Features list:
   
   **Report Analysis (NLP Route)**
   - PDF sustainability report analysis
   - Environmental metric extraction
   - Greenwashing detection
   - Risk scoring
   
   **Emissions Calculator (Structured Data Route)** ← NEW
   - Activity-based emissions calculation
   - Support for CSV/Excel bulk upload
   - Scope 1, 2, 3 breakdown
   - UK DEFRA 2024 emission factors
   
   **Verification Engine** ← NEW
   - Compare reported claims vs calculated emissions
   - Discrepancy detection and severity scoring
   - Recommendations for investigation

2. Update "How It Works" section:

   Carbon Compass has two complementary analysis routes:
   
   **Route 1: Report Analysis**
   Upload a sustainability report PDF → NLP extracts metrics → 
   Greenwashing detection → Risk score
   
   **Route 2: Emissions Calculator**
   Input activity data (energy, fuel, travel, waste) → 
   Calculate emissions using DEFRA factors → 
   Get Scope 1, 2, 3 breakdown
   
   **Verification**
   Compare Route 1 (what companies claim) against Route 2 
   (what the numbers show) → Find discrepancies

3. Add new API endpoints to the table:

   | Method | Endpoint | Description |
   |--------|----------|-------------|
   | POST | /api/v1/calculate/single | Calculate single activity |
   | POST | /api/v1/calculate/bulk | Calculate multiple activities |
   | POST | /api/v1/calculate/upload | Calculate from CSV/Excel |
   | GET | /api/v1/calculate/factors | List emission factors |
   | POST | /api/v1/verify/{filename} | Verify report against data |

4. Add "Data Sources" section:

   Emission factors sourced from:
   - UK DEFRA Greenhouse Gas Reporting Factors 2024
   - IEA Emissions Factors 2024 (electricity grids)
   - IPCC Guidelines for National GHG Inventories

5. Update screenshots placeholder to include calculator and verification pages.

Keep the README professional and scannable.
```

---

## Data Collection Checklist

Before running Prompt 21, download and prepare:

### Required: UK DEFRA 2024 Conversion Factors

1. Go to: https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024
2. Download the Excel file
3. Extract these values for your JSON files:
   - Fuels sheet → fuels.json
   - Electricity sheet → UK value for electricity.json
   - Business travel - air sheet → transport.json (flights)
   - Business travel - land sheet → transport.json (road, rail)
   - Waste disposal sheet → waste.json
   - Water supply/treatment sheet → water.json

### Required: Electricity Grid Factors by Country

1. Go to: https://www.iea.org/data-and-statistics/data-product/emissions-factors-2024
   - (Free registration may be required)
2. Or use these approximate 2024 values (already included in Prompt 21):
   - Sri Lanka: 0.731 kg CO2e/kWh
   - UK: 0.207
   - US: 0.417
   - UAE: 0.442
   - And others listed in the prompt

### Optional: Industry Benchmarks

For future benchmarking features:
- CDP Sector Benchmarks: https://www.cdp.net/en/research
- Science Based Targets database: https://sciencebasedtargets.org/companies-taking-action

---

## Timeline for Structured Data Route

| Day | Tasks |
|-----|-------|
| 1 | Download DEFRA data, create JSON factor files (Prompt 21) |
| 2 | Build calculator service and activity parser (Prompts 22-23) |
| 3 | Build verification engine and API routes (Prompts 24-25) |
| 4 | Build calculator frontend pages (Prompts 26-27) |
| 5 | Build verification frontend and update navigation (Prompts 28-29) |
| 6 | Database updates and documentation (Prompts 30-31) |

---

## Testing Checklist for Structured Data Route

**Calculator**
- [ ] Single activity calculation works (electricity, fuel, transport, waste, water)
- [ ] Correct emission factors applied
- [ ] Scope classification correct (1, 2, or 3)
- [ ] Unit conversions work (litres/gallons, km/miles)
- [ ] Bulk calculation sums correctly

**File Upload**
- [ ] CSV parsing works
- [ ] Excel parsing works
- [ ] Column auto-detection works
- [ ] Invalid rows flagged with clear errors
- [ ] Template download works

**Verification**
- [ ] Compares NLP metrics to calculated values
- [ ] Discrepancies detected and severity assigned
- [ ] Match score calculation reasonable
- [ ] Recommendations generated

**Frontend**
- [ ] Calculator form works end-to-end
- [ ] Scope breakdown chart renders
- [ ] Verification page shows comparison
- [ ] Navigation updated with new pages

---

## Interview Talking Points (Updated)

**Elevator Pitch (Updated):**
"Carbon Compass has two routes: it analyses what companies claim in their sustainability reports using NLP, and it independently calculates what their emissions should be using activity data and official conversion factors. Then it compares the two to find discrepancies — essentially fact-checking corporate climate claims."

**Technical Depth:**
- "The calculator uses UK DEFRA 2024 emission factors, which are the UK government's official conversion rates"
- "Scope classification follows the GHG Protocol: Scope 1 is direct emissions, Scope 2 is purchased energy, Scope 3 is value chain"
- "The verification engine allows tolerance thresholds because methodologies vary — we flag anything over 25% difference as major"

**Why Two Routes:**
- "Reports tell you what companies want you to see. The calculator tells you what the math says. Comparing them reveals the truth gap."
- "This is exactly what ESG analysts do manually — we're automating that forensic comparison."

---

Good luck with the Structured Data route! 🧭
