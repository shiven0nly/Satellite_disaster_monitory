"use client";

import React from "react";
import { JobStatus } from "@/types";

interface UploadProgressProps {
  jobId: string | null;
  status: JobStatus | null;
  isPolling: boolean;
  attemptCount: number;
  maxAttempts?: number;
  error: string | null;
  timedOut: boolean;
  onRetry: () => void;
  onReset: () => void;
}

export default function UploadProgress({
  jobId,
  status,
  isPolling,
  attemptCount,
  maxAttempts = 30,
  error,
  timedOut,
  onRetry,
  onReset,
}: UploadProgressProps) {
  const isFailed = status === JobStatus.FAILED || !!error || timedOut;
  const progressPercent = Math.min(Math.round((attemptCount / maxAttempts) * 100), 95);

  return (
    <div className="p-8 rounded-2xl bg-[#131b2e] border border-[#1e293b] space-y-6 shadow-xl">
      {/* Header Status Bar */}
      <div className="flex items-center justify-between border-b border-[#1e293b] pb-4">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${
            isFailed
              ? "bg-rose-500"
              : status === JobStatus.COMPLETED
              ? "bg-emerald-400"
              : "bg-cyan-400 animate-ping"
          }`}></div>
          <div>
            <h3 className="text-sm font-bold text-slate-100">
              {isFailed
                ? "Analysis Failed"
                : status === JobStatus.PROCESSING
                ? "Parsing Satellite Imagery with AI..."
                : status === JobStatus.PENDING
                ? "Job Enqueued in Background Queue"
                : "Uploading Image File..."}
            </h3>
            {jobId && (
              <p className="text-xs font-mono text-cyan-400 mt-0.5">
                Job ID: #{jobId}
              </p>
            )}
          </div>
        </div>

        {/* Polling Count Badge */}
        {!isFailed && (
          <div className="text-xs font-mono px-3 py-1 rounded-md bg-[#080c14] border border-[#1e293b] text-slate-400">
            Poll Attempt: <span className="text-cyan-400 font-bold">{attemptCount}</span> / {maxAttempts}
          </div>
        )}
      </div>

      {/* Error / Timeout Display State */}
      {isFailed ? (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm space-y-2">
            <div className="font-semibold flex items-center gap-2 text-rose-400">
              <svg className="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{timedOut ? "Processing Timeout" : "Model Analysis Failed"}</span>
            </div>
            <p className="text-xs text-rose-200 leading-relaxed pl-7">
              {error || "An unexpected error occurred during disaster analysis."}
            </p>
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onReset}
              className="px-4 py-2 rounded-lg bg-[#080c14] hover:bg-[#101726] border border-[#1e293b] text-slate-300 text-xs font-semibold transition"
            >
              Upload Different Image
            </button>
            <button
              type="button"
              onClick={onRetry}
              className="px-5 py-2 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold transition flex items-center gap-2"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Retry Status Poll
            </button>
          </div>
        </div>
      ) : (
        /* Animated Progress Bar */
        <div className="space-y-3">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">
              {isPolling ? "Checking job result..." : "Submitting payload..."}
            </span>
            <span className="text-cyan-400 font-mono font-bold">{progressPercent}%</span>
          </div>

          <div className="w-full h-3 rounded-full bg-[#080c14] border border-[#1e293b] overflow-hidden relative">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 to-violet-600 transition-all duration-500 rounded-full shadow-[0_0_12px_rgba(6,182,212,0.6)]"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>

          <p className="text-[11px] text-slate-400 text-center pt-2">
            The FastAPI backend process is running mocked segmentation and thermal hazard analysis.
          </p>
        </div>
      )}
    </div>
  );
}
