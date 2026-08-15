import React from "react";
import Link from "next/link";
import { JobRead } from "@/types";
import { getSeverityTheme } from "@/lib/severity";

interface MarkerPopupProps {
  job: JobRead;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

function getFullImageUrl(url?: string) {
  if (!url) return null;
  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }
  return `${API_BASE_URL}${url.startsWith("/") ? "" : "/"}${url}`;
}

export default function MarkerPopup({ job }: MarkerPopupProps) {
  const result = job.result;
  const imageUrl = getFullImageUrl(job.image_url);
  const severityTheme = getSeverityTheme(result?.severity);

  const confidencePct =
    result?.confidence_score !== undefined && result?.confidence_score !== null
      ? `${Math.round(result.confidence_score * 100)}%`
      : "N/A";

  return (
    <div className="p-1 min-w-[210px] max-w-[250px] text-slate-100 font-sans">
      {/* Thumbnail Image */}
      {imageUrl ? (
        <div className="w-full h-28 rounded-lg overflow-hidden bg-[#080c14] border border-[#1e293b] mb-3 relative">
          {/* eslint-disable-next-html-element-suppression */}
          <img
            src={imageUrl}
            alt={result?.disaster_type || "Disaster Satellite Image"}
            className="w-full h-full object-cover"
          />
          <div className="absolute top-1.5 left-1.5 px-2 py-0.5 rounded bg-black/70 backdrop-blur-xs text-[10px] font-mono text-cyan-300 uppercase">
            {job.image_type || "OPTICAL"}
          </div>
        </div>
      ) : (
        <div className="w-full h-20 rounded-lg bg-[#080c14] border border-[#1e293b] mb-3 flex items-center justify-center text-slate-500 text-[11px] italic">
          No image preview available
        </div>
      )}

      {/* Disaster Header & Info */}
      <div className="space-y-1.5 mb-3">
        <div className="flex items-center justify-between gap-2">
          <h3 className="font-bold text-sm text-slate-100 truncate capitalize">
            {result?.disaster_type || "Detected Anomaly"}
          </h3>
          <span
            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${severityTheme.bg} ${severityTheme.text} ${severityTheme.border}`}
          >
            {result?.severity || "MEDIUM"}
          </span>
        </div>

        <div className="text-[11px] font-mono text-slate-400 flex items-center justify-between">
          <span>Confidence Score:</span>
          <span className="text-cyan-400 font-bold">{confidencePct}</span>
        </div>

        {result?.latitude !== undefined && result?.longitude !== undefined && (
          <div className="text-[10px] font-mono text-slate-400 truncate">
            Lat: {result.latitude?.toFixed(4)}°, Lng: {result.longitude?.toFixed(4)}°
          </div>
        )}
      </div>

      {/* View Full Report Link */}
      <Link
        href={`/results/${job.id}`}
        className="w-full block text-center py-1.5 px-3 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold transition"
      >
        View Full Report →
      </Link>
    </div>
  );
}
