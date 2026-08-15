"use client";

import React, { useState, useEffect, useCallback } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { listJobs, ApiError } from "@/lib/api";
import { JobRead } from "@/types";

const DisasterMap = dynamic(() => import("@/components/DisasterMap"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[550px] rounded-2xl bg-[#131b2e] border border-[#1e293b] flex items-center justify-center text-slate-400 text-sm animate-pulse">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
        <span>Initializing Leaflet GIS Engine...</span>
      </div>
    </div>
  ),
});

export default function MapPage() {
  const [jobs, setJobs] = useState<JobRead[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMapJobs = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Fetch up to 100 jobs to display on geospatial map
      const response = await listJobs(1, 100);
      setJobs(response.jobs || []);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`[HTTP ${err.status}] ${err.message}`);
      } else {
        setError("Failed to load disaster analysis records for map.");
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMapJobs();
  }, [fetchMapJobs]);

  // Filter jobs with valid coordinates
  const validJobs = jobs.filter(
    (j) =>
      j.result &&
      j.result.latitude !== undefined &&
      j.result.latitude !== null &&
      j.result.longitude !== undefined &&
      j.result.longitude !== null &&
      !isNaN(j.result.latitude) &&
      !isNaN(j.result.longitude)
  );

  // Check if all mock results currently share identical latitude & longitude
  const duplicateLocationDetected =
    validJobs.length > 1 &&
    validJobs.every(
      (j) =>
        j.result?.latitude === validJobs[0].result?.latitude &&
        j.result?.longitude === validJobs[0].result?.longitude
    );

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e293b] pb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight flex items-center gap-3">
            Geospatial Disaster Map
          </h1>
          <p className="text-slate-400 mt-2 text-sm max-w-2xl">
            Interactive map overlay of satellite analysis targets, thermal anomalies, and flood extent markers color-coded by severity.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 text-xs font-mono">
            PLOTTED MARKERS: {validJobs.length} / {jobs.length}
          </span>
        </div>
      </div>

      {/* Warning banner if backend mock data duplicate locations detected */}
      {duplicateLocationDetected && (
        <div className="p-4 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-200 text-xs space-y-1">
          <div className="font-bold flex items-center gap-2 text-amber-300">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Mock Backend Coordinate Overlap Notice
          </div>
          <p>
            All currently fetched mock jobs share identical latitude/longitude coordinates (34.0522°, -118.2437°). Markers will overlap at the exact same location until varied mock coordinates or live backend data are introduced.
          </p>
        </div>
      )}

      {/* Error alert if fetch fails */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center justify-between">
          <span>{error}</span>
          <button
            onClick={fetchMapJobs}
            className="px-3 py-1 bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 text-xs font-semibold rounded transition"
          >
            Retry
          </button>
        </div>
      )}

      {/* Main Interactive Map Component */}
      {isLoading ? (
        <div className="w-full h-[550px] rounded-2xl bg-[#131b2e] border border-[#1e293b] flex items-center justify-center text-slate-400 text-sm animate-pulse">
          Loading map data...
        </div>
      ) : (
        <DisasterMap jobs={jobs} />
      )}

      {/* Page Footer Info */}
      <div className="flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 pt-4 border-t border-[#1e293b] gap-2">
        <div>
          Tile Provider: <span className="text-slate-300">CartoDB Dark Matter</span> (OpenStreetMap) | Projection: <span className="text-slate-300">EPSG:4326</span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/upload" className="hover:text-cyan-400 transition">Upload New Satellite Data</Link>
          <span>•</span>
          <Link href="/history" className="hover:text-cyan-400 transition">View History Table</Link>
        </div>
      </div>
    </div>
  );
}
