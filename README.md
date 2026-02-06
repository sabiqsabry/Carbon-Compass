# 🧭 Carbon Compass

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18-61dafb.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0-3178c6.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**AI-Powered Sustainability Report Analyser & Emissions Calculator**

*Analyse reports, calculate emissions, and verify corporate climate claims — all in one platform.*

[Features](#-features) • [How It Works](#-how-it-works) • [Quick Start](#-quick-start) • [Tech Stack](#-tech-stack) • [API](#-api-endpoints)

</div>

---

## 🚀 Overview

**Carbon Compass** has two complementary analysis routes: it analyses what companies **claim** in their sustainability reports using NLP, and it independently **calculates** what their emissions should be using activity data and official conversion factors. Then it **compares** the two to find discrepancies — essentially fact-checking corporate climate claims.

### ✨ Key Features

**Report Analysis (NLP Route)**
- **📄 Document Intelligence**: Automatically parses complex PDFs and extracts structured data
- **🌱 Metric Extraction**: Identifies Carbon Emissions (Scopes 1, 2, 3), Energy, Water, and Waste usage
- **🚩 Greenwashing Detector**: Flags vague claims, missing baselines, and unsubstantiated promises
- **⚖️ Risk Scoring**: Calculates a transparent risk score (0-100) based on data quality and commitment levels
- **🤝 Company Comparison**: Compare environmental performance across multiple organisations side-by-side

**Emissions Calculator (Structured Data Route)**
- **🧮 Activity-Based Calculation**: Compute emissions from energy, fuel, transport, waste, and water data
- **📊 Scope 1, 2, 3 Breakdown**: Automatic classification following the GHG Protocol
- **📁 Bulk Upload**: CSV/Excel file upload with auto-detection of column mappings
- **🌍 Country-Specific Factors**: Electricity grid factors for 27+ countries (IEA/DEFRA 2024)

**Verification Engine**
- **🔍 Claim Verification**: Compare NLP-extracted report claims against calculated emissions
- **⚠️ Discrepancy Detection**: Automatically flag and classify mismatches by severity
- **💡 Actionable Recommendations**: Suggestions for investigation based on findings

---

## 🔄 How It Works

Carbon Compass has two complementary analysis routes:

```
┌─────────────────────────────────────────────────────────────────┐
│                        CARBON COMPASS                           │
├─────────────────────────────┬───────────────────────────────────┤
│       NLP ROUTE             │    STRUCTURED DATA ROUTE          │
│  (What companies CLAIM)     │   (What the numbers SHOW)         │
├─────────────────────────────┼───────────────────────────────────┤
│ • PDF report analysis       │ • Activity data input             │
│ • Metric extraction         │ • Emissions calculation           │
│ • Greenwashing detection    │ • DEFRA 2024 conversion factors   │
│ • Risk scoring              │ • CSV/Excel bulk upload           │
├─────────────────────────────┴───────────────────────────────────┤
│                    VERIFICATION ENGINE                           │
│       Compare extracted claims vs calculated actuals             │
│            Flag discrepancies • Verify accuracy                  │
└─────────────────────────────────────────────────────────────────┘
```

**Route 1 — Report Analysis:** Upload a sustainability report PDF → NLP extracts metrics → Greenwashing detection → Risk score

**Route 2 — Emissions Calculator:** Input activity data (energy, fuel, travel, waste) → Calculate emissions using DEFRA factors → Get Scope 1, 2, 3 breakdown

**Verification:** Compare Route 1 (what companies claim) against Route 2 (what the numbers show) → Find discrepancies

---

## 📊 Data Sources

Emission factors are sourced from:
- **UK DEFRA** Greenhouse Gas Reporting Conversion Factors 2024
- **IEA** Emissions Factors 2024 (electricity grids by country)
- **IPCC** Guidelines for National GHG Inventories

---

## 🛠️ Tech Stack

| Component | Technologies |
|-----------|--------------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy, PyMuPDF, spaCy, HuggingFace Transformers |
| **Frontend** | React 19, TypeScript, Tailwind CSS 4, Recharts, React Query |
| **Database** | PostgreSQL, Supabase (AsyncPG), SQLite fallback |
| **AI/ML** | BERT-based models for summarisation and classification |
| **Data** | UK DEFRA 2024, IEA 2024, US EPA emission factors |

---

## ⚡ Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **Supabase Account** (Optional, for persistence)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_md
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit **http://localhost:5173** to access the application.

---

## 📖 Usage Guide

### Report Analysis
1.  **Upload**: Drag & drop a PDF sustainability report on the Upload page
2.  **Analyse**: Click "Analyse Now" to let the AI process the document
3.  **Insights**: View extracted metrics, risk scores, and greenwashing flags
4.  **Compare**: Select multiple reports to compare performance against competitors

### Emissions Calculator
1.  **Manual Entry**: Add activities one-by-one (electricity, fuel, transport, waste, water)
2.  **Bulk Upload**: Upload a CSV or Excel file with activity data
3.  **Results**: View total emissions with Scope 1, 2, 3 breakdown chart

### Verification
1.  **Select Report**: Choose a previously analysed sustainability report
2.  **Enter Activity Data**: Input the actual activity data for comparison
3.  **Review**: See match score, discrepancies, and recommendations

---

## 🔌 API Endpoints

### Report Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/upload` | Upload a new PDF report |
| `POST` | `/api/v1/analyse/{id}` | Trigger full AI analysis |
| `GET` | `/api/v1/analysis/{id}` | Retrieve analysis results |
| `GET` | `/api/v1/analysis/{id}/metrics` | Get extracted metrics |
| `GET` | `/api/v1/analysis/{id}/greenwashing` | Get greenwashing flags |
| `GET` | `/api/v1/analysis/{id}/risk` | Get risk score |
| `POST` | `/api/v1/compare` | Compare multiple reports |

### Emissions Calculator

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/calculate/single` | Calculate emissions for a single activity |
| `POST` | `/api/v1/calculate/bulk` | Calculate emissions for multiple activities |
| `POST` | `/api/v1/calculate/upload` | Calculate from CSV/Excel file upload |
| `POST` | `/api/v1/calculate/upload/preview` | Preview uploaded file before calculating |
| `GET` | `/api/v1/calculate/factors` | List available emission factors |
| `GET` | `/api/v1/calculate/countries` | List countries with electricity factors |

### Verification

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/verify/{filename}` | Verify report claims against activity data |
| `GET` | `/api/v1/verify/{filename}/summary` | Get report metrics summary for verification |

---

<div align="center">
Built by <a href="https://sabiq.dev/" target="_blank">Sabiq Sabry</a>
</div>
