import Link from "next/link";

export default function HomePage() {
  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Hero / Page Heading */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e293b] pb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight flex items-center gap-3">
            Satellite Disaster Monitoring Dashboard
          </h1>
          <p className="text-slate-400 mt-2 text-sm max-w-2xl">
            Real-time AI parsing and analysis of optical, infrared, and thermal satellite imagery for emergency disaster response and damage estimation.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/upload"
            className="px-4 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-white font-semibold text-sm transition shadow-lg shadow-cyan-500/25 flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            Upload Satellite Image
          </Link>
        </div>
      </div>

      {/* Overview Stat Cards Placeholder */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="p-5 rounded-xl bg-[#131b2e] border border-[#1e293b] space-y-2">
          <div className="text-xs text-slate-400 font-medium">Total Images Processed</div>
          <div className="text-2xl font-bold text-cyan-400">142</div>
          <div className="text-[11px] text-emerald-400 flex items-center gap-1">
            <span>↑ 12% from last week</span>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-[#131b2e] border border-[#1e293b] space-y-2">
          <div className="text-xs text-slate-400 font-medium">Active Wildfire Anomalies</div>
          <div className="text-2xl font-bold text-amber-400">8</div>
          <div className="text-[11px] text-slate-400">Thermal hotspots flagged</div>
        </div>

        <div className="p-5 rounded-xl bg-[#131b2e] border border-[#1e293b] space-y-2">
          <div className="text-xs text-slate-400 font-medium">Flood Zones Detected</div>
          <div className="text-2xl font-bold text-violet-400">19</div>
          <div className="text-[11px] text-slate-400">Estimated 340 sq km</div>
        </div>

        <div className="p-5 rounded-xl bg-[#131b2e] border border-[#1e293b] space-y-2">
          <div className="text-xs text-slate-400 font-medium">AI Confidence Average</div>
          <div className="text-2xl font-bold text-emerald-400">94.8%</div>
          <div className="text-[11px] text-slate-400">Validated by ground sensors</div>
        </div>
      </div>

      {/* Module Overview Quick Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
        <div className="p-6 rounded-xl bg-[#131b2e] border border-[#1e293b] hover:border-cyan-500/40 transition group">
          <div className="w-12 h-12 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-4 group-hover:scale-105 transition">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </div>
          <h2 className="text-lg font-bold text-slate-100 mb-2">Upload & Analyze</h2>
          <p className="text-sm text-slate-400 mb-4">
            Upload optical, thermal, or IR satellite frames for AI disaster segmentations.
          </p>
          <Link href="/upload" className="text-sm font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1">
            Go to Upload →
          </Link>
        </div>

        <div className="p-6 rounded-xl bg-[#131b2e] border border-[#1e293b] hover:border-violet-500/40 transition group">
          <div className="w-12 h-12 rounded-lg bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-400 mb-4 group-hover:scale-105 transition">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-lg font-bold text-slate-100 mb-2">Past Analyses</h2>
          <p className="text-sm text-slate-400 mb-4">
            Review history logs, exported reports, and historical disaster trends.
          </p>
          <Link href="/history" className="text-sm font-semibold text-violet-400 hover:text-violet-300 flex items-center gap-1">
            Browse History →
          </Link>
        </div>

        <div className="p-6 rounded-xl bg-[#131b2e] border border-[#1e293b] hover:border-emerald-500/40 transition group">
          <div className="w-12 h-12 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4 group-hover:scale-105 transition">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l5.447 2.724A1 1 0 0021 18.764V7.982a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
          </div>
          <h2 className="text-lg font-bold text-slate-100 mb-2">Monitoring Map</h2>
          <p className="text-sm text-slate-400 mb-4">
            View geo-tagged disaster zones, thermal hotspot markers, and affected radii.
          </p>
          <Link href="/map" className="text-sm font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
            Open Map View →
          </Link>
        </div>
      </div>
    </div>
  );
}
