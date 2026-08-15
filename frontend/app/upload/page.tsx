"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import UploadDropzone from "@/components/UploadDropzone";
import UploadProgress from "@/components/UploadProgress";
import { usePollJobStatus } from "@/hooks/usePollJobStatus";
import { uploadImage, ApiError } from "@/lib/api";
import { ImageType, JobStatus } from "@/types";

export default function UploadPage() {
  const router = useRouter();

  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Custom hook polling backend GET /results/{jobId} every 2 seconds
  const {
    status,
    isPolling,
    error: pollError,
    attemptCount,
    timedOut,
    restartPolling,
  } = usePollJobStatus(activeJobId);

  // Navigate automatically to results page upon COMPLETED status
  useEffect(() => {
    if (activeJobId && status === JobStatus.COMPLETED) {
      router.push(`/results/${activeJobId}`);
    }
  }, [activeJobId, status, router]);

  const handleFileSubmit = async (file: File, imageType: ImageType) => {
    setIsUploading(true);
    setUploadError(null);

    try {
      const response = await uploadImage(file, imageType);
      setActiveJobId(response.id);
    } catch (err) {
      if (err instanceof ApiError) {
        setUploadError(`[HTTP ${err.status}] ${err.message}`);
      } else {
        setUploadError("Failed to upload image. Please verify your connection.");
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleReset = () => {
    setActiveJobId(null);
    setIsUploading(false);
    setUploadError(null);
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Page Header */}
      <div className="border-b border-[#1e293b] pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight flex items-center gap-3">
            Upload & Analyze Imagery
          </h1>
          <p className="text-slate-400 mt-2 text-sm max-w-2xl">
            Submit optical, thermal, or infrared satellite frames to execute background AI disaster segmentation and hotspot detection.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded bg-violet-500/10 text-violet-300 border border-violet-500/30 text-xs font-mono">
            MAX FILE SIZE: 20MB
          </span>
        </div>
      </div>

      {/* Main Container State Switch */}
      {uploadError ? (
        <div className="p-8 rounded-2xl bg-[#131b2e] border border-rose-500/30 space-y-4">
          <div className="flex items-center gap-3 text-rose-400">
            <svg className="w-6 h-6 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h3 className="text-base font-bold">Upload Encountered an Error</h3>
          </div>
          <p className="text-sm text-slate-300 pl-9">{uploadError}</p>
          <div className="pl-9 pt-2">
            <button
              type="button"
              onClick={handleReset}
              className="px-5 py-2.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold transition"
            >
              Try Uploading Again
            </button>
          </div>
        </div>
      ) : activeJobId ? (
        <UploadProgress
          jobId={activeJobId}
          status={status}
          isPolling={isPolling}
          attemptCount={attemptCount}
          maxAttempts={30}
          error={pollError}
          timedOut={timedOut}
          onRetry={restartPolling}
          onReset={handleReset}
        />
      ) : (
        <UploadDropzone
          onFileSubmit={handleFileSubmit}
          isUploading={isUploading}
        />
      )}
    </div>
  );
}
