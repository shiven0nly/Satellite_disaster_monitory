import Link from "next/link";

export default function HistoryPage() {
  // Placeholder table records
  const sampleHistory = [
    { id: "job-101", title: "California Wildfire Sensor Feed", type: "Wildfire", date: "2026-08-14", status: "Completed", severity: "High" },
    { id: "job-102", title: "Monsoon Flood Inundation Region B", type: "Flood", date: "2026-08-13", status: "Completed", severity: "Medium" },
    { id: "job-103", title: "Coastal Thermal Anomaly Pass #4", type: "Thermal", date: "2026-08-12", status: "Processing", severity: "Low" },
    { id: "job-104", title: "Landslide Slope Hazard Assessment", type: "Landslide", date: "2026-08-10", status: "Completed", severity: "Critical" },
  ];

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="border-b border-[#1e293b] pb-6">
        <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight">
          Past Disaster Analyses
        </h1>
        <p className="text-slate-400 mt-2 text-sm">
          Browse historical satellite image parsing records, model logs, and analytical reports.
        </p>
      </div>

      {/* Table Container Placeholder */}
      <div className="rounded-xl bg-[#131b2e] border border-[#1e293b] overflow-hidden">
        <div className="p-4 border-b border-[#1e293b] flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
            Analysis History Log (Placeholder Data)
          </h2>
          <span className="text-xs text-slate-400 font-mono">Showing 4 recent jobs</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-[#0e1424] text-xs uppercase text-slate-400 border-b border-[#1e293b]">
              <tr>
                <th className="px-6 py-3.5">Job ID</th>
                <th className="px-6 py-3.5">Analysis Title</th>
                <th className="px-6 py-3.5">Type</th>
                <th className="px-6 py-3.5">Date</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e293b]">
              {sampleHistory.map((item) => (
                <tr key={item.id} className="hover:bg-[#1c263f] transition-colors">
                  <td className="px-6 py-4 font-mono text-cyan-400 text-xs">{item.id}</td>
                  <td className="px-6 py-4 font-medium text-slate-100">{item.title}</td>
                  <td className="px-6 py-4 text-xs text-slate-300">{item.type}</td>
                  <td className="px-6 py-4 text-xs text-slate-400">{item.date}</td>
                  <td className="px-6 py-4 text-xs">
                    <span className={`px-2.5 py-1 rounded-full font-semibold ${
                      item.status === "Completed"
                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                        : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                    }`}>
                      {item.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      href={`/results/${item.id}`}
                      className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 bg-cyan-500/10 hover:bg-cyan-500/20 px-3 py-1.5 rounded border border-cyan-500/30 transition"
                    >
                      View Report →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
