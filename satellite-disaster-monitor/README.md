# Satellite Disaster Monitoring System

A monorepo workspace for satellite disaster monitoring consisting of a FastAPI backend and a Streamlit frontend dashboard managed strictly with `uv`.

## Directory Structure

```text
satellite-disaster-monitor/
├── pyproject.toml          (uv workspace root)
├── uv.lock
├── .python-version
├── .gitignore
├── README.md
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── model.py         (trained model wrapper placeholder)
│   │   ├── llm_service.py   (Groq integration placeholder)
│   │   └── schemas.py       (Pydantic schemas)
│   └── .env.example
└── frontend/
    ├── pyproject.toml
    ├── app.py
    ├── utils/
    │   ├── __init__.py
    │   ├── api_client.py
    │   └── charts.py
    └── .streamlit/
        └── config.toml
```

## Getting Started

### 1. Setup & Installation

All dependencies and virtual environments are managed using `uv`.

Root setup:
```bash
uv sync
```

### 2. Running Backend (FastAPI)

```bash
cd backend
uv run uvicorn app.main:app --reload
```

### 3. Running Frontend (Streamlit)

```bash
cd frontend
uv run streamlit run app.py
```
