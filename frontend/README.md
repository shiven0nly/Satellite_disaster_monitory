# Satellite Disaster Monitoring Frontend

A dark, space-themed Next.js 14+ (App Router) dashboard skeleton for satellite imagery disaster analysis, thermal hotspot detection, flood segmentation, and geospatial monitoring.

## 📁 Directory Structure

```text
frontend/
├── app/
│   ├── layout.tsx             # Root layout with persistent Sidebar
│   ├── page.tsx               # Dashboard Home page
│   ├── globals.css            # Dark space baseline theme & glassmorphism
│   ├── upload/
│   │   └── page.tsx           # Upload & Analyze page
│   ├── results/
│   │   └── [jobId]/
│   │       └── page.tsx       # Single disaster analysis result (dynamic route)
│   ├── history/
│   │   └── page.tsx           # Past disaster analyses table
│   └── map/
│       └── page.tsx           # Geospatial monitoring map view
├── components/
│   └── Sidebar.tsx            # Persistent dark space sidebar navigation
├── lib/
│   └── api.ts                 # FastAPI client placeholder functions
├── types/
│   └── index.ts               # Shared TypeScript domain interfaces
├── tailwind.config.ts         # Space theme colors (space-bg, space-accent, etc.)
├── package.json               # Next.js & Tailwind setup
└── .env.local.example         # Environment variable templates
```

## 🚀 How to Run Locally

### 1. Configure Environment Variables
Copy `.env.local.example` to `.env.local`:
```bash
cp .env.local.example .env.local
```
Ensure `NEXT_PUBLIC_API_BASE_URL` points to your running FastAPI backend (defaults to `http://localhost:8000`).

### 2. Install Dependencies
```bash
npm install
```

### 3. Run Development Server
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) with your browser to view the application.

## 🎨 Space Theme Colors
Custom colors configured in `tailwind.config.ts`:
- `space-bg`: `#080c14` (Deep space navy/black background)
- `space-sidebar`: `#0e1424` (Sidebar container navy)
- `space-card`: `#131b2e` (Card element background)
- `space-accent`: `#06b6d4` (Cyan glowing accent)
- `space-violet`: `#8b5cf6` (Violet accent)
- `space-emerald`: `#10b981` (Online/Thermal success accent)
- `space-border`: `#1e293b` (Subtle dark blue border)
