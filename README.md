# 🧭 Carbon Compass

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18-61dafb.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0-3178c6.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**AI-Powered Sustainability Report Analyser**

*Transforming 100+ page corporate sustainability reports into digestible insights in seconds.*

[Features](#-features) • [Quick Start](#-quick-start) • [Tech Stack](#-tech-stack) • [API](#-api-endpoints)

</div>

---

## 🚀 Overview

**Carbon Compass** is an intelligent tool that leverages Natural Language Processing (NLP) to analyze corporate sustainability reports (ESG, CSR). It automatically extracts critical environmental metrics, detects greenwashing attempts, calculates risk scores, and allows for side-by-side company comparisons.

### ✨ Key Features

- **📄 Document Intelligence**: Automatically parses complex PDFs and extracts structured data.
- **🌱 Metric Extraction**: Identifies Carbon Emissions (Scopes 1, 2, 3), Energy, Water, and Waste usage.
- **🚩 Greenwashing Detector**: Flags vague claims ("eco-friendly"), missing baselines, and unsubstantiated promises.
- **⚖️ Risk Scoring**: Calculates a transparent risk score (0-100) based on data quality and commitment levels.
- **📊 Interactive Dashboard**: Visualizes data with dynamic charts and gauges.
- **🤝 Company Comparison**: Compare environmental performance across multiple organizations side-by-side.

---

## 🛠️ Tech Stack

| Component | Technologies |
|-----------|--------------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy, PyMuPDF, spaCy, HuggingFace Transformers |
| **Frontend** | React 18, TypeScript, Tailwind CSS, Recharts, React Query |
| **Database** | PostgreSQL, Supabase (AsyncPG) |
| **AI/ML** | BERT-based models for summarization and classification |

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

1.  **Upload**: Drag & drop a PDF sustainability report on the Upload page.
2.  **Analyze**: Click "Analyse Now" to let the AI process the document.
3.  **Insights**: View extracted metrics, risk scores, and greenwashing flags.
4.  **Compare**: Select multiple reports to compare performance against competitors.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/upload` | Upload a new PDF report |
| `POST` | `/api/v1/analyse/{id}` | Trigger full AI analysis |
| `GET`  | `/api/v1/analysis/{id}` | Retrieve analysis results |
| `POST` | `/api/v1/compare` | Compare multiple reports |

---

<div align="center">
Built by <a href="https://sabiq.dev/" target="_blank">Sabiq Sabry</a>
</div>
