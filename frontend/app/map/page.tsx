export default function MapPage() {
  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e293b] pb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight flex items-center gap-3">
            Geospatial Monitoring Map
          </h1>
          <p className="text-slate-400 mt-2 text-sm">
            Interactive map overlay of active satellite passes, thermal anomalies, and flood extent markers.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 text-xs font-mono">
            GEO-PROJECTION: WGS 84 / EPSG:4326
          </span>
        </div>
      </div>

      {/* Map Canvas Container Placeholder */}
      <div className="p-6 rounded-2xl bg-[#131b2e] border border-[#1e293b] space-y-4">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-4">
            <span className="font-semibold text-slate-200">Layer Controls:</span>
            <label className="flex items-center gap-1.5 cursor-pointer text-slate-300">
              <input type="checkbox" defaultChecked className="rounded border-[#1e293b] accent-cyan-500" />
              Thermal Hotspots
            </label>
            <label className="flex items-center gap-1.5 cursor-pointer text-slate-300">
              <input type="checkbox" defaultChecked className="rounded border-[#1e293b] accent-violet-500" />
              Flood Boundaries
            </label>
          </div>
          <span className="text-emerald-400 font-mono flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            Live GPS Feed Sync
          </span>
        </div>

        {/* Map Visual Box Placeholder */}
        <div className="w-full h-[450px] rounded-xl bg-[#0e1424] border border-[#1e293b] relative overflow-hidden flex flex-col items-center justify-center">
          {/* Decorative Map Grid & Target Reticle */}
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(#06b6d4_1px,transparent_1px)] [background-size:24px_24px]"></div>

          <div className="z-10 flex flex-col items-center gap-3 text-center p-8 max-w-md">
            <div className="w-16 h-16 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-lg shadow-cyan-500/10">
              <svg className="w-8 h-8 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            
            <h2 className="text-lg font-bold text-slate-200">Interactive Map View Placeholder</h2>
            <p className="text-xs text-slate-400 leading-relaxed">
              Mapbox / Leaflet / OpenLayers rendering engine will be initialized here in the map integration step to plot geo-referenced TIFF polygons and satellite pins.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
