"use client";

import React from "react";
import { JobStatus, SeverityLevel } from "@/types";

interface HistoryFiltersProps {
  selectedDisaster: string;
  selectedSeverity: string;
  selectedStatus: string;
  onDisasterChange: (val: string) => void;
  onSeverityChange: (val: string) => void;
  onStatusChange: (val: string) => void;
  onResetFilters: () => void;
}

/**
 * Filter dropdown controls for past disaster analyses.
 * NOTE: Currently filtering is applied client-side on the current page slice.
 * If the dataset grows significantly, server-side filtering via /jobs?status=...
 * can be passed directly to the backend listJobs endpoint.
 */
export default function HistoryFilters({
  selectedDisaster,
  selectedSeverity,
  selectedStatus,
  onDisasterChange,
  onSeverityChange,
  onStatusChange,
  onResetFilters,
}: HistoryFiltersProps) {
  const hasActiveFilters =
    selectedDisaster !== "ALL" ||
    selectedSeverity !== "ALL" ||
    selectedStatus !== "ALL";

  return (
    <div className="p-4 rounded-xl bg-[#131b2e] border border-[#1e293b] flex flex-wrap items-center justify-between gap-4">
      <div className="flex flex-wrap items-center gap-3">
        {/* Disaster Type Filter */}
        <div>
          <label className="block text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
            Disaster Type
          </label>
          <select
            value={selectedDisaster}
            onChange={(e) => onDisasterChange(e.target.value)}
            className="bg-[#080c14] border border-[#1e293b] rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 transition"
          >
            <option value="ALL">All Categories</option>
            <option value="wildfire">Wildfire</option>
            <option value="flood">Flood</option>
            <option value="hurricane">Hurricane</option>
            <option value="earthquake">Earthquake</option>
            <option value="landslide">Landslide</option>
            <option value="thermal">Thermal Anomaly</option>
          </select>
        </div>

        {/* Severity Filter */}
        <div>
          <label className="block text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
            Severity
          </label>
          <select
            value={selectedSeverity}
            onChange={(e) => onSeverityChange(e.target.value)}
            className="bg-[#080c14] border border-[#1e293b] rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 transition"
          >
            <option value="ALL">All Severities</option>
            <option value={SeverityLevel.LOW}>Low</option>
            <option value={SeverityLevel.MEDIUM}>Medium</option>
            <option value={SeverityLevel.HIGH}>High</option>
            <option value={SeverityLevel.CRITICAL}>Critical</option>
          </select>
        </div>

        {/* Status Filter */}
        <div>
          <label className="block text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
            Status
          </label>
          <select
            value={selectedStatus}
            onChange={(e) => onStatusChange(e.target.value)}
            className="bg-[#080c14] border border-[#1e293b] rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 transition"
          >
            <option value="ALL">All Statuses</option>
            <option value={JobStatus.COMPLETED}>Completed</option>
            <option value={JobStatus.PROCESSING}>Processing</option>
            <option value={JobStatus.PENDING}>Pending</option>
            <option value={JobStatus.FAILED}>Failed</option>
          </select>
        </div>
      </div>

      {hasActiveFilters && (
        <button
          onClick={onResetFilters}
          className="text-xs text-rose-400 hover:text-rose-300 font-medium transition flex items-center gap-1"
        >
          Reset Filters
        </button>
      )}
    </div>
  );
}
