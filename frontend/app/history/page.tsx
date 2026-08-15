"use client";

import React, { useState, useEffect, Suspense, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import HistoryFilters from "@/components/HistoryFilters";
import HistoryTable from "@/components/HistoryTable";
import PaginationControls from "@/components/PaginationControls";
import { listJobs, ApiError } from "@/lib/api";
import { JobRead } from "@/types";

const PAGE_SIZE = 10;

function HistoryContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Read current page from URL params (?page=X)
  const pageParam = searchParams.get("page");
  const currentPage = pageParam ? Math.max(1, parseInt(pageParam, 10) || 1) : 1;

  const [jobs, setJobs] = useState<JobRead[]>([]);
  const [totalJobs, setTotalJobs] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Client-side filter states
  const [selectedDisaster, setSelectedDisaster] = useState<string>("ALL");
  const [selectedSeverity, setSelectedSeverity] = useState<string>("ALL");
  const [selectedStatus, setSelectedStatus] = useState<string>("ALL");

  const loadJobs = useCallback(async (page: number) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await listJobs(page, PAGE_SIZE);
      setJobs(response.jobs);
      setTotalJobs(response.total);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`[HTTP ${err.status}] ${err.message}`);
      } else {
        setError("Failed to load disaster analysis history.");
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadJobs(currentPage);
  }, [currentPage, loadJobs]);

  const handlePageChange = (newPage: number) => {
    router.push(`/history?page=${newPage}`);
  };

  const handleResetFilters = () => {
    setSelectedDisaster("ALL");
    setSelectedSeverity("ALL");
    setSelectedStatus("ALL");
  };

  // Filter jobs based on client dropdown selection
  const filteredJobs = jobs.filter((job) => {
    const result = job.result;

    if (
      selectedDisaster !== "ALL" &&
      result?.disaster_type?.toLowerCase() !== selectedDisaster.toLowerCase()
    ) {
      return false;
    }

    if (
      selectedSeverity !== "ALL" &&
      result?.severity?.toUpperCase() !== selectedSeverity.toUpperCase()
    ) {
      return false;
    }

    if (
      selectedStatus !== "ALL" &&
      job.status?.toUpperCase() !== selectedStatus.toUpperCase()
    ) {
      return false;
    }

    return true;
  });

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="border-b border-[#1e293b] pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight flex items-center gap-3">
            Past Disaster Analyses
          </h1>
          <p className="text-slate-400 mt-2 text-sm max-w-2xl">
            Browse and query historical satellite image parsing records, model logs, and damage evaluations.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 text-xs font-mono">
            TOTAL RECORDS: {totalJobs}
          </span>
        </div>
      </div>

      {/* Filter Controls Bar */}
      <HistoryFilters
        selectedDisaster={selectedDisaster}
        selectedSeverity={selectedSeverity}
        selectedStatus={selectedStatus}
        onDisasterChange={setSelectedDisaster}
        onSeverityChange={setSelectedSeverity}
        onStatusChange={setSelectedStatus}
        onResetFilters={handleResetFilters}
      />

      {/* Error Alert if Fetch Fails */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center justify-between">
          <span>{error}</span>
          <button
            onClick={() => loadJobs(currentPage)}
            className="px-3 py-1 bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 text-xs font-semibold rounded transition"
          >
            Retry
          </button>
        </div>
      )}

      {/* Data Table */}
      <HistoryTable jobs={filteredJobs} isLoading={isLoading} />

      {/* Pagination Bar */}
      {!isLoading && totalJobs > 0 && (
        <PaginationControls
          currentPage={currentPage}
          totalItems={totalJobs}
          pageSize={PAGE_SIZE}
          onPageChange={handlePageChange}
        />
      )}
    </div>
  );
}

export default function HistoryPage() {
  return (
    <Suspense
      fallback={
        <div className="p-8 text-center text-slate-400 text-sm animate-pulse">
          Loading history dashboard...
        </div>
      }
    >
      <HistoryContent />
    </Suspense>
  );
}
