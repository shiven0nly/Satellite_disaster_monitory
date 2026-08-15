# satellite-disaster-backend

FastAPI backend service for satellite image analysis, disaster monitoring, and structured insights.

## Project Structure

```text
backend/
├── alembic/
│   ├── versions/
│   │   └── .gitkeep
│   ├── env.py
│   └── script.py.mako
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── health.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── health.py
│   └── services/
│       └── __init__.py
├── .env.example
├── alembic.ini
├── README.md
└── requirements.txt
```

---

## Local Setup & Quickstart

### 1. Prerequisites
- **Python 3.11+** installed
- **PostgreSQL 14+** database running locally or remotely

---

### 2. Environment Configuration
Copy the `.env.example` file to create your local `.env` configuration file:

```bash
cp .env.example .env
```

Update `.env` with your local PostgreSQL credentials:
- `POSTGRES_SERVER`: Host IP or hostname (e.g., `localhost`)
- `POSTGRES_PORT`: Port (default `5432`)
- `POSTGRES_USER`: PostgreSQL user (e.g., `postgres`)
- `POSTGRES_PASSWORD`: Your PostgreSQL password
- `POSTGRES_DB`: Your PostgreSQL database name (e.g., `satellite_disaster_db`)

---

### 3. Create Virtual Environment & Install Dependencies

#### PowerShell (Windows):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

#### Bash/Zsh (Linux/macOS):
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4. Running Database Migrations

Make sure your PostgreSQL database exists before running Alembic migrations:

```bash
# Generate initial migration when new models are added
alembic revision --autogenerate -m "Initial schema setup"

# Apply migrations to database
alembic upgrade head
```

---

### 5. Running the Application Server

Start the Uvicorn development server with auto-reload:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

### 6. Verification & Interactive API Documentation

- **Health Check Endpoint**:  
  `GET http://127.0.0.1:8000/health`

- **Swagger UI Interactive Docs**:  
  `http://127.0.0.1:8000/api/v1/docs`

- **ReDoc Interactive Docs**:  
  `http://127.0.0.1:8000/api/v1/redoc`
