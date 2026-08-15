"use client";

/**
 * SERVER vs CLIENT COMPONENT DECISION:
 * This page is implemented as a Client Component because:
 * 1. Dynamic Polling: If a user navigates directly or refreshes the page while a job is still
 *    in PENDING or PROCESSING status, the component relies on `usePollJobStatus` hook to poll
 *    the backend every 2 seconds until COMPLETED or FAILED, preventing dead/stale states.
 * 2. Interactive UI: Enables interactive polling controls, error retries, and overlay toggles.
 */

import React, { use } from "react";
import Link from "next/link";
import SeverityBadge from "@/components/SeverityBadge";
import ConfidenceBar from "@/components/ConfidenceBar";
import UploadProgress from "@/components/UploadProgress";
import { usePollJobStatus } from "@/hooks/usePollJobStatus";
import { JobStatus } from "@/types";

interface PageProps {
  params: Promise<{
    jobId: string;
  }>;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function JobResultPage({ params }: PageProps) {
  const { jobId } = use(params);

  // Hook polls GET /results/{jobId} every 2s if status is PENDING or PROCESSING
  const {
    job,
    status,
    isPolling,
    error,
    attemptCount,
    timedOut,
    restartPolling,
  } = usePollJobStatus(jobId);

  // Helper to resolve image URL (whether relative or absolute)
  const getFullImageUrl = (url?: string) => {
    if (!url) return null;
    if (url.startsWith("http://") || url.startsWith("https://")) {
      return url;
    }
    return `${API_BASE_URL}${url.startsWith("/") ? "" : "/"}${url}`;
  };

  // 1. Error / Failed / 404 State
  if (error || status === JobStatus.FAILED || timedOut) {
    return (
      <div className="space-y-8 max-w-4xl mx-auto py-6">
        <div className="flex items-center justify-between border-b border-[#1e293b] pb-6">
          <div>
            <div className="text-xs font-mono text-rose-400 mb-1">JOB ID: #{jobId}</div>
            <h1 className="text-3xl font-extrabold text-slate-100">Analysis Error</h1>
          </div>
          <Link
            href="/history"
            className="px-4 py-2 rounded-lg bg-[#131b2e] border border-[#1e293b] text-slate-300 text-xs font-semibold hover:bg-[#1c263f] transition"
          >
            ← Back to History
          </Link>
        </div>

        <div className="p-8 rounded-2xl bg-[#131b2e] border border-rose-500/30 space-y-5">
          <div className="flex items-center gap-3 text-rose-400">
            <svg className="w-6 h-6 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h2 className="text-lg font-bold">Unable to Display Job Results</h2>
          </div>

          <p className="text-sm text-slate-300 leading-relaxed pl-9">
            {error || "The specified disaster job could not be retrieved or failed during model inference."}
          </p>

          <div className="flex items-center gap-4 pl-9 pt-3">
            <button
              onClick={restartPolling}
              className="px-5 py-2.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold transition"
            >
              Retry Status Fetch
            </button>
            <Link
              href="/upload"
              className="px-5 py-2.5 rounded-xl bg-[#080c14] hover:bg-[#101726] border border-[#1e293b] text-slate-300 text-xs font-semibold transition"
            >
              Upload New Image
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // 2. Active Polling / In-Progress State
  if (status === JobStatus.PENDING || status === JobStatus.PROCESSING || (!job && isPolling)) {
    return (
      <div className="space-y-8 max-w-4xl mx-auto py-6">
        <div className="border-b border-[#1e293b] pb-6">
          <div className="text-xs font-mono text-cyan-400 mb-1">JOB ID: #{jobId}</div>
          <h1 className="text-3xl font-extrabold text-slate-100">Analyzing Satellite Data...</h1>
        </div>

        <UploadProgress
          jobId={jobId}
          status={status}
          isPolling={isPolling}
          attemptCount={attemptCount}
          maxAttempts={30}
          error={error}
          timedOut={timedOut}
          onRetry={restartPolling}
          onReset={restartPolling}
        />
      </div>
    );
  }

  // 3. Initial Loading Skeleton (before initial fetch completes)
  if (!job) {
    return (
      <div className="space-y-8 max-w-6xl mx-auto animate-pulse">
        <div className="h-10 bg-[#131b2e] w-1/3 rounded-lg"></div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-96 bg-[#131b2e] rounded-xl"></div>
          <div className="h-96 bg-[#131b2e] rounded-xl"></div>
        </div>
      </div>
    );
  }

  const result = job.result;
  const imageUrl = getFullImageUrl(job.image_url);

  // 4. Success State (COMPLETED)
  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e293b] pb-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 mb-1">
            <span>JOB ID:</span>
            <span className="bg-cyan-500/10 px-2.5 py-0.5 rounded border border-cyan-500/30">
              #{job.id}
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight flex items-center gap-3">
            {result?.disaster_type ? `${result.disaster_type} Analysis Report` : "Disaster Analysis Result"}
          </h1>
          <p className="text-slate-400 mt-1 text-xs font-mono">
            Analyzed at: {new Date(result?.created_at || job.created_at).toLocaleString()}
          </p>
        </div>

        {/* Severity Badge Header */}
        <div className="flex items-center gap-3">
          {result?.severity && <SeverityBadge severity={result.severity} />}
        </div>
      </div>

      {/* Main Grid: Image Viewer & Parsed AI Report */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2 Cols): Satellite Image Viewer */}
        <div className="lg:col-span-2 space-y-4">
          <div className="p-5 rounded-2xl bg-[#131b2e] border border-[#1e293b] space-y-4 shadow-xl">
            <div className="flex items-center justify-between text-xs text-slate-400 border-b border-[#1e293b] pb-3">
              <span className="font-semibold text-slate-200 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                Processed Raster Imagery
              </span>
              <span className="font-mono text-cyan-400 uppercase">
                Band: {job.image_type || "OPTICAL"}
              </span>
            </div>

            {/* Satellite Image Display Box with Bounding Box Overlay Marker */}
            <div className="w-full min-h-[350px] max-h-[500px] rounded-xl bg-[#080c14] border border-[#1e293b] relative overflow-hidden flex items-center justify-center group">
              {imageUrl ? (
                /* eslint-disable-next-html-element-suppression */
                <img
                  src={imageUrl}
                  alt={`Satellite Image for Job ${job.id}`}
                  className="w-full h-full object-contain max-h-[480px]"
                />
              ) : (
                <div className="text-center p-8 text-slate-400 text-xs">
                  Imagery render unavailable
                </div>
              )}

              {/* Simulated Geo-spatial Detection Overlay Box */}
              {result && (
                <div className="absolute inset-8 border-2 border-dashed border-cyan-400/70 rounded-lg pointer-events-none flex items-start justify-end p-2 bg-cyan-500/5 shadow-[0_0_20px_rgba(6,182,212,0.15)]">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-500/40">
                    DETECTED REGION
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column (1 Col): AI Analytics Summary */}
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#131b2e] border border-[#1e293b] space-y-5 shadow-xl">
            <h2 className="text-base font-bold text-slate-100 border-b border-[#1e293b] pb-3 flex items-center gap-2">
              <svg className="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              AI Parsing Summary
            </h2>

            <div className="space-y-4">
              {/* Disaster Classification */}
              <div>
                <span className="text-xs text-slate-400 block mb-1 font-medium">Disaster Category</span>
                <span className="text-lg font-extrabold text-cyan-300 capitalize tracking-tight">
                  {result?.disaster_type || "Unclassified Anomaly"}
                </span>
              </div>

              {/* Confidence Bar Component */}
              <ConfidenceBar score={result?.confidence_score} />

              {/* Affected Area Estimate */}
              <div className="pt-2 border-t border-[#1e293b]/60">
                <span className="text-xs text-slate-400 block mb-1 font-medium">Affected Area Estimate</span>
                <span className="text-sm font-bold text-slate-200 font-mono">
                  {result?.affected_area_estimate ? result.affected_area_estimate : "Not estimated"}
                </span>
              </div>

              {/* Lat / Long Coordinates */}
              <div className="pt-2 border-t border-[#1e293b]/60">
                <span className="text-xs text-slate-400 block mb-1 font-medium">Geo Coordinates</span>
                {result?.latitude !== undefined && result?.latitude !== null && result?.longitude !== undefined && result?.longitude !== null ? (
                  <span className="text-xs font-mono text-cyan-300 bg-[#080c14] px-2.5 py-1 rounded border border-[#1e293b] inline-block">
                    Lat: {result.latitude.toFixed(4)}°, Lng: {result.longitude.toFixed(4)}°
                  </span>
                ) : (
                  <span className="text-xs text-slate-400 italic">Location coordinates not available</span>
                )}
              </div>
            </div>

            {/* Description Text */}
            <div className="pt-4 border-t border-[#1e293b] space-y-1.5">
              <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider block">
                Model Synthesis Description
              </span>
              <p className="text-xs text-slate-300 leading-relaxed bg-[#080c14] p-3.5 rounded-xl border border-[#1e293b]">
                {result?.description || "No description generated by model."}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Navigation Toolbar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-6 border-t border-[#1e293b]">
        <Link
          href="/upload"
          className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-xs font-semibold transition flex items-center justify-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          ← Upload Another Image
        </Link>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <Link
            href="/history"
            className="flex-1 sm:flex-initial px-5 py-2.5 rounded-xl bg-[#131b2e] hover:bg-[#1c263f] text-slate-300 border border-[#1e293b] text-xs font-semibold transition text-center"
          >
            View in History
          </Link>
          <Link
            href="/map"
            className="flex-1 sm:flex-initial px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-white text-xs font-semibold transition shadow-lg shadow-cyan-500/20 text-center"
          >
            View on Map →
          </Link>
        </div>
      </div>
    </div>
  );
}
