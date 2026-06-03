<div align="center">

# 🎮 Video Games Analytics

**End-to-end data pipeline — REST API — Interactive dashboard**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit)](https://streamlit.io)
[![DuckDB](https://img.shields.io/badge/DuckDB-0.10-FFF000?logo=duckdb)](https://duckdb.org)
[![PySpark](https://img.shields.io/badge/PySpark-3.5-E25A1C?logo=apachespark)](https://spark.apache.org)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.13-005571?logo=elasticsearch)](https://elastic.co)

<br/>

> **Author:** Japhet Allah-n'diguim &nbsp;·&nbsp; Data Engineer  
> *Designing robust pipelines, scalable storage, and analytical APIs from raw data to insight.*

</div>

---

## 📌 Overview

A production-grade video game sales analytics platform designed to demonstrate the full scope of a **Data Engineering** workflow — from raw ingestion to queryable, visualized output.

The pipeline ingests a 16,000+ row Kaggle dataset, applies cleaning and feature engineering, and exposes the results through three layers: a **SQL analytics engine** (DuckDB), a **full-text search index** (Elasticsearch), and a **big-data processing layer** (PySpark). A FastAPI REST backend and a Streamlit dashboard sit on top for consumption.

> **Dataset:** 16,593 video game titles · 11 raw columns · global + regional sales across all major platforms (1980–2020)

---

## 🖼️ Dashboard Preview

> Pages exported from the live Streamlit dashboard. Click any link to open the full PDF.

| Page | Description |
|------|-------------|
| [📊 Overview](images/vue ensemble.pdf) | Global KPIs, top games, sales summary |
| [🎮 Genre Analysis](images/Genres et Plateformes.pdf) | Sales by genre, avg performance, top titles per genre |
| [🏢 Publisher Rankings](images/editeurs.pdf) | Publisher leaderboard, blockbuster counts, genre diversity |
| [🌍 Regional Sales](images/regions.pdf) | NA / EU / JP / Other breakdown and comparisons |
| [📅 Temporal Trends](images/temps.pdf) | Year-over-year sales evolution by decade and genre |
| [🔍 Game Explorer](images/classement.pdf) | Filterable game table with search and export |

> ⚠️ Rename the filenames above to match your actual PDFs in the `images/` folder.

---

## 🏗️ Architecture

The project follows a **layered data engineering architecture**: ingestion → transformation → storage → serving.

```
                    ┌──────────────┐
                    │  Raw CSV     │
                    │  (Kaggle)    │
                    └──────┬───────┘
                           │  Ingestion
                    ┌──────▼───────┐
                    │ Data Loader  │  schema validation, type casting
                    └──────┬───────┘
                           │  Transformation
                    ┌──────▼───────┐
                    │ Data Cleaner │  dedup, imputation, feature engineering
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │  Analytics / Storage
       ┌──────▼─────┐ ┌───▼────┐ ┌────▼─────┐
       │ DuckDB     │ │ Spark  │ │ Web      │
       │ SQL engine │ │ Proc.  │ │ Scraper  │
       └──────┬─────┘ └───┬────┘ └────┬─────┘
              │            │            │
              └────────────┼────────────┘
                           │  Indexing
                    ┌──────▼───────┐
                    │ Elasticsearch│  full-text search indexing
                    │   Indexer    │
                    └──────┬───────┘
                           │  Serving
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼─────┐ ┌───▼────┐ ┌────▼─────┐
       │ FastAPI    │ │Streamlit│ │ Notebook │
       │ REST API   │ │Dashboard│ │  EDA     │
       └────────────┘ └────────┘ └──────────┘
```

### Data Engineering Highlights

- **Idempotent pipeline** — re-running `run_projet.py` is safe; intermediate files are overwritten cleanly
- **Columnar storage** — cleaned data persisted as **Parquet** via PyArrow for fast downstream reads
- **In-process OLAP** — DuckDB enables sub-second aggregations on 16K+ rows without a server
- **Dual-store design** — structured queries via DuckDB + unstructured search via Elasticsearch
- **Orchestrated execution** — a single entry point (`run_projet.py`) sequences pipeline → API → dashboard with configurable flags

---

## 🗂️ Project Structure

```
videogames-analytics/
├── api/                          # Serving layer — FastAPI backend
│   ├── main.py                   # REST endpoints: /games, /search, /stats
│   ├── models.py                 # Pydantic request/response schemas
│   └── database.py               # DuckDB connection management
├── dashboard/                    # Visualization layer — Streamlit
│   ├── app.py                    # Main dashboard app
│   └── components.py             # Reusable chart components
├── scripts/                      # Pipeline layer — data engineering
│   ├── data_loader.py            # CSV ingestion & schema validation
│   ├── data_cleaner.py           # Cleaning, imputation, dedup, feature engineering
│   ├── web_scraper.py            # Wikipedia scraping (best-selling games)
│   ├── duckdb_queries.py         # SQL analytics (genre, publisher, temporal)
│   ├── elasticsearch_indexer.py  # Full-text search indexing
│   └── spark_processor.py        # PySpark big-data processing & outlier detection
├── data/
│   ├── raw/                      # Source CSV (never modified)
│   ├── processed/                # Cleaned Parquet output
│   ├── enriched/                 # Enriched datasets (Spark output)
│   └── videogames.db             # DuckDB analytical database
├── images/                       # Dashboard PDF exports
├── notebooks/
│   └── exploration.py            # Exploratory data analysis
├── tests/
│   └── test_scraper.py           # Unit tests
├── run_projet.py                 # Orchestrator: pipeline → API → dashboard
├── requirements.txt
└── .gitignore
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- (Optional) [Elasticsearch](https://elastic.co) 8.x for full-text search
- Dataset: [`video_games_sales.csv` from Kaggle](https://www.kaggle.com/datasets/gregorut/videogamesales) → place in `data/raw/`

### Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\Activate.ps1    # Windows PowerShell

pip install -r requirements.txt
```

### Run Everything

```bash
python run_projet.py
```

This single command orchestrates the full stack in sequence:

| Step | What happens |
|------|-------------|
| 1️⃣ Data pipeline | Loads → cleans → deduplicates → enriches → writes Parquet + DuckDB |
| 2️⃣ FastAPI | REST API live at `http://127.0.0.1:8000` · docs at `/docs` |
| 3️⃣ Streamlit | Interactive dashboard at `http://localhost:8501` |

### Selective Execution

```bash
# Pipeline only (no services)
python run_projet.py --pipeline

# Services only (skip pipeline)
python run_projet.py --skip-pipeline

# API only
python run_projet.py --api

# Dashboard only
python run_projet.py --dashboard
```

### Manual Start

```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
streamlit run dashboard/app.py
```

---

## 🌐 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API health check |
| `GET` | `/games` | List games with pagination and filters |
| `GET` | `/games/{id}` | Retrieve a single game by ID |
| `GET` | `/search?q=` | Full-text search via Elasticsearch |
| `GET` | `/stats/overview` | Aggregate KPIs (total sales, game count, etc.) |

Interactive Swagger docs: `http://127.0.0.1:8000/docs`

---

## 📊 Pipeline Output — Key Numbers

| Metric | Value |
|--------|-------|
| Raw rows ingested | 16,598 |
| Rows after deduplication | 16,593 (-5) |
| Unique publishers analyzed | 234 |
| Top-selling title | Wii Sports — 82.74M copies |
| Highest avg-sales genre | Platform — 0.94M / game |
| Most prolific publisher | Nintendo — 702 games, 1,786M total sales |
| Decade with most releases | 2000s |

---

## 🛠️ Tech Stack

| Layer | Tools & Rationale |
|-------|-------------------|
| **Ingestion** | Pandas, PyArrow — fast CSV parsing, columnar Parquet output |
| **Transformation** | Pandas, NumPy — cleaning, imputation, feature engineering |
| **OLAP / SQL** | DuckDB — in-process analytical SQL, no server needed |
| **Big data** | PySpark 3.5 — distributed processing, outlier detection |
| **Search** | Elasticsearch 8.x — full-text indexing and fuzzy search |
| **API** | FastAPI + Uvicorn + Pydantic — typed, async REST layer |
| **Dashboard** | Streamlit, Plotly, Altair — interactive data visualization |
| **Scraping** | Requests, BeautifulSoup, lxml — Wikipedia enrichment |
| **Observability** | Loguru — structured logging throughout the pipeline |

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 📊 Example Use Cases

- Identify best-selling games by genre, platform, and decade
- Analyze global vs. regional sales split (NA / EU / JP / Other)
- Full-text game search by title, publisher, or genre
- Detect top performers and outliers using Spark analytics
- Benchmark publisher performance: release volume vs. commercial impact

---

## 👤 Author

**Japhet Allah-n'diguim**  
Data Engineer — pipeline design · analytical databases · REST APIs · data visualization

---

## 📝 License

MIT