import Link from "next/link";

interface JobResultPageProps {
  params: Promise<{
    jobId: string;
  }>;
}

export default async function JobResultPage({ params }: JobResultPageProps) {
  const { jobId } = await params;

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e293b] pb-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 mb-1">
            <span>JOB ID:</span>
            <span className="bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">#{jobId}</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight">
            Disaster Analysis Result
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/history"
            className="px-4 py-2 rounded-lg bg-[#131b2e] border border-[#1e293b] hover:bg-[#1c263f] text-slate-300 text-sm font-medium transition"
          >
            ← Back to History
          </Link>
        </div>
      </div>

      {/* Grid Placeholder: Image viewer & AI report */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Imagery Viewer Placeholder */}
        <div className="lg:col-span-2 space-y-4">
          <div className="p-4 rounded-xl bg-[#131b2e] border border-[#1e293b] space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold text-slate-200">Satellite Image Overlay</span>
              <span>Band: Thermal IR (Band 10/11)</span>
            </div>
            
            {/* Visual Frame Placeholder */}
            <div className="w-full h-80 rounded-lg bg-[#0e1424] border border-[#1e293b] flex flex-col items-center justify-center relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-tr from-cyan-950/30 via-slate-900 to-violet-950/30 opacity-70"></div>
              <div className="z-10 flex flex-col items-center gap-2 text-center p-6">
                <svg className="w-12 h-12 text-cyan-400/80 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l5.447 2.724A1 1 0 0021 18.764V7.982a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
                <span className="text-sm font-semibold text-slate-300">
                  Satellite Image & Mask Overlay Placeholder
                </span>
                <span className="text-xs text-slate-400">
                  (Job <code className="text-cyan-400">{jobId}</code> imagery will be rendered here upon backend connection)
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Col: AI Summary & Metrics */}
        <div className="space-y-4">
          <div className="p-5 rounded-xl bg-[#131b2e] border border-[#1e293b] space-y-4">
            <h2 className="text-md font-bold text-slate-200 border-b border-[#1e293b] pb-2">
              AI Parsing Summary
            </h2>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-400">Disaster Classification</span>
                <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 font-semibold">
                  Wildfire / Thermal Hotspot
                </span>
              </div>

              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-400">Confidence Score</span>
                <span className="font-bold text-emerald-400">96.4%</span>
              </div>

              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-400">Affected Perimeter</span>
                <span className="font-mono text-cyan-300">42.8 sq km</span>
              </div>

              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-400">Severity Level</span>
                <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-semibold">
                  HIGH
                </span>
              </div>
            </div>

            <div className="pt-2 border-t border-[#1e293b]">
              <div className="text-xs font-semibold text-slate-400 mb-1">Recommended Response</div>
              <p className="text-xs text-slate-300 leading-relaxed bg-[#0e1424] p-3 rounded-lg border border-[#1e293b]">
                Deploy emergency containment teams to Northwest quadrant. Thermal plume expanding towards populated zone.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
