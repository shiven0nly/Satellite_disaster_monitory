"use client";

import React from "react";
import Link from "next/link";
import SeverityBadge from "@/components/SeverityBadge";
import { JobRead, JobStatus } from "@/types";

interface HistoryTableProps {
  jobs: JobRead[];
  isLoading: boolean;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

// Relative time formatting helper
function formatRelativeTime(dateString: string): string {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 30) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  } catch {
    return dateString;
  }
}

export default function HistoryTable({ jobs, isLoading }: HistoryTableProps) {
  const getFullImageUrl = (url?: string) => {
    if (!url) return null;
    if (url.startsWith("http://") || url.startsWith("https://")) {
      return url;
    }
    return `${API_BASE_URL}${url.startsWith("/") ? "" : "/"}${url}`;
  };

  // Skeleton row renderer
  if (isLoading) {
    return (
      <div className="rounded-xl bg-[#131b2e] border border-[#1e293b] overflow-hidden">
        <div className="p-4 space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-12 bg-[#080c14] rounded-lg animate-pulse"></div>
          ))}
        </div>
      </div>
    );
  }

  // Empty state renderer
  if (!jobs || jobs.length === 0) {
    return (
      <div className="p-12 rounded-xl bg-[#131b2e] border border-[#1e293b] text-center space-y-4">
        <div className="w-16 h-16 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 mx-auto">
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <h3 className="text-base font-bold text-slate-100">No Disaster Analyses Found</h3>
        <p className="text-xs text-slate-400 max-w-sm mx-auto">
          No records matched your query or filter criteria. Upload a new satellite image frame to initiate AI detection.
        </p>
        <div>
          <Link
            href="/upload"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-white font-semibold text-xs transition shadow-lg shadow-cyan-500/20"
          >
            Upload Satellite Image →
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl bg-[#131b2e] border border-[#1e293b] overflow-hidden shadow-xl">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-[#080c14] text-xs uppercase tracking-wider text-slate-400 border-b border-[#1e293b]">
            <tr>
              <th className="px-5 py-3.5">Thumbnail</th>
              <th className="px-5 py-3.5">Job ID</th>
              <th className="px-5 py-3.5">Disaster Type</th>
              <th className="px-5 py-3.5">Severity</th>
              <th className="px-5 py-3.5">Confidence</th>
              <th className="px-5 py-3.5">Status</th>
              <th className="px-5 py-3.5">Analyzed</th>
              <th className="px-5 py-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1e293b]/70">
            {jobs.map((job) => {
              const result = job.result;
              const imageUrl = getFullImageUrl(job.image_url);
              const confidence = result?.confidence_score
                ? `${(result.confidence_score > 1 ? result.confidence_score : result.confidence_score * 100).toFixed(1)}%`
                : "N/A";

              return (
                <tr key={job.id} className="hover:bg-[#1c263f] transition-colors group">
                  {/* Thumbnail */}
                  <td className="px-5 py-3">
                    <div className="w-12 h-10 rounded-lg bg-[#080c14] border border-[#1e293b] overflow-hidden flex items-center justify-center relative">
                      {imageUrl ? (
                        /* eslint-disable-next-html-element-suppression */
                        <img
                          src={imageUrl}
                          alt="Thumb"
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <svg className="w-5 h-5 text-cyan-400/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      )}
                    </div>
                  </td>

                  {/* Job ID */}
                  <td className="px-5 py-3 font-mono text-xs text-cyan-400">
                    #{job.id.substring(0, 8)}
                  </td>

                  {/* Disaster Type */}
                  <td className="px-5 py-3 font-semibold text-slate-100 capitalize">
                    {result?.disaster_type || "Unclassified"}
                  </td>

                  {/* Severity Badge */}
                  <td className="px-5 py-3">
                    {result?.severity ? (
                      <SeverityBadge severity={result.severity} />
                    ) : (
                      <span className="text-xs text-slate-400 italic">Pending</span>
                    )}
                  </td>

                  {/* Confidence */}
                  <td className="px-5 py-3 font-mono text-xs font-bold text-emerald-400">
                    {confidence}
                  </td>

                  {/* Status */}
                  <td className="px-5 py-3 text-xs">
                    <span className={`px-2.5 py-1 rounded-full font-semibold ${
                      job.status === JobStatus.COMPLETED
                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                        : job.status === JobStatus.FAILED
                        ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                        : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                    }`}>
                      {job.status}
                    </span>
                  </td>

                  {/* Created At */}
                  <td className="px-5 py-3 text-xs text-slate-400 font-mono">
                    {formatRelativeTime(job.created_at)}
                  </td>

                  {/* Action */}
                  <td className="px-5 py-3 text-right">
                    <Link
                      href={`/results/${job.id}`}
                      className="px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-xs font-semibold transition"
                    >
                      View Report →
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
