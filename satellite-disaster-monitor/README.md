# Deployment Guide: Satellite Disaster Monitoring System

This project is separated into a **FastAPI backend** (hosted on Render, Railway, or Fly.io) and a **Streamlit frontend dashboard** (hosted on Streamlit Community Cloud).

---

## 1. Backend Deployment (Render / Railway / Fly.io)

Since Streamlit Community Cloud only hosts Streamlit applications, deploy the FastAPI backend service to a platform like Render or Railway.

### Deployment Options & Start Command:
- **Build Command**: `uv sync` (or `pip install -r backend/requirements.txt`)
- **Start Command**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
- **Root Directory**: `satellite-disaster-monitor/backend`

### Environment Variables:
Set the following environment variables in your backend hosting platform dashboard:
- `GROQ_API_KEY`: Your actual Groq API key (`gsk_...`)
- `HOST`: `0.0.0.0`

---

## 2. Frontend Deployment (Streamlit Community Cloud)

Streamlit Community Cloud expects a `requirements.txt` file located in the application directory.

### Deployment Steps:
1. Push your repository to GitHub.
2. Log into [share.streamlit.io](https://share.streamlit.io/).
3. Click **New App** and select your repository & branch.
4. Set the configuration options:
   - **Main file path**: `frontend/app.py`
   - **App directory**: `frontend` (Streamlit will locate `frontend/requirements.txt`)
5. **Advanced Settings -> Secrets**:
   Add your deployed backend URL:
   ```toml
   BACKEND_URL = "https://your-backend-api.onrender.com"
   ```
6. Click **Deploy!**

---

## 🔒 Security Notes
- Real credentials and `secrets.toml` are explicitly ignored in `.gitignore`.
- Always use `secrets.toml.example` and `.env.example` as reference templates for environment variable setup.
