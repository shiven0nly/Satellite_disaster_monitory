"use client";

import React from "react";

interface PaginationControlsProps {
  currentPage: number;
  totalItems: number;
  pageSize: number;
  onPageChange: (newPage: number) => void;
}

export default function PaginationControls({
  currentPage,
  totalItems,
  pageSize,
  onPageChange,
}: PaginationControlsProps) {
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const hasPrev = currentPage > 1;
  const hasNext = currentPage < totalPages;

  return (
    <div className="p-4 rounded-xl bg-[#131b2e] border border-[#1e293b] flex items-center justify-between">
      <div className="text-xs text-slate-400 font-mono">
        Showing page <span className="text-slate-100 font-bold">{currentPage}</span> of{" "}
        <span className="text-slate-100 font-bold">{totalPages}</span> ({totalItems} total records)
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={!hasPrev}
          className="px-3.5 py-1.5 rounded-lg bg-[#080c14] border border-[#1e293b] text-xs font-semibold text-slate-300 hover:bg-[#101726] hover:text-white disabled:opacity-40 disabled:cursor-not-allowed transition"
        >
          ← Prev
        </button>

        <span className="px-3 py-1 text-xs font-mono text-cyan-400 bg-cyan-500/10 rounded border border-cyan-500/30">
          {currentPage}
        </span>

        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={!hasNext}
          className="px-3.5 py-1.5 rounded-lg bg-[#080c14] border border-[#1e293b] text-xs font-semibold text-slate-300 hover:bg-[#101726] hover:text-white disabled:opacity-40 disabled:cursor-not-allowed transition"
        >
          Next →
        </button>
      </div>
    </div>
  );
}
