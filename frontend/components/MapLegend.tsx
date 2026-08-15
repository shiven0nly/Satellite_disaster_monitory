import React from "react";
import { severityColors } from "@/lib/severity";

export default function MapLegend() {
  return (
    <div className="absolute bottom-4 right-4 z-[1000] bg-[#131b2e]/90 backdrop-blur-md border border-[#1e293b] p-3.5 rounded-xl shadow-2xl text-xs space-y-2 max-w-[200px] pointer-events-auto">
      <div className="font-semibold text-slate-200 border-b border-[#1e293b] pb-1.5 flex items-center justify-between">
        <span>Severity Scale</span>
        <span className="text-[10px] text-slate-400 font-mono">EPSG:4326</span>
      </div>
      <div className="space-y-1.5 pt-0.5">
        {Object.entries(severityColors).map(([key, config]) => (
          <div key={key} className="flex items-center justify-between text-slate-300 text-[11px]">
            <div className="flex items-center gap-2">
              <span
                className="w-3 h-3 rounded-full border border-white/20 shadow-sm shrink-0"
                style={{ backgroundColor: config.hex }}
              />
              <span className="font-medium">{config.name}</span>
            </div>
            <span className="text-[10px] font-mono text-slate-400 uppercase">{key}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
