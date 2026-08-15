"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { getJobResult, ApiError } from "@/lib/api";
import { JobRead, JobStatus } from "@/types";

const POLL_INTERVAL_MS = 2000;
const MAX_POLL_ATTEMPTS = 30; // 30 attempts * 2s = 60s timeout

interface UsePollJobStatusReturn {
  job: JobRead | null;
  status: JobStatus | null;
  isPolling: boolean;
  error: string | null;
  attemptCount: number;
  timedOut: boolean;
  restartPolling: () => void;
}

/**
 * Custom hook to poll GET /results/{jobId} every 2 seconds until:
 * - Status is COMPLETED or FAILED
 * - Max attempts limit (30) is reached (timeout)
 * 
 * NOTE ON WEBSOCKETS:
 * While WebSockets could provide real-time streaming updates for long-running ML tasks,
 * polling is used here to match the current FastAPI HTTP REST architecture. WebSockets
 * can be added as a future optimization when a WS gateway endpoint is added.
 */
export function usePollJobStatus(jobId: string | null): UsePollJobStatusReturn {
  const [job, setJob] = useState<JobRead | null>(null);
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [isPolling, setIsPolling] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [attemptCount, setAttemptCount] = useState<number>(0);
  const [timedOut, setTimedOut] = useState<boolean>(false);

  const attemptsRef = useRef<number>(0);

  const poll = useCallback(async () => {
    if (!jobId) return;

    if (attemptsRef.current >= MAX_POLL_ATTEMPTS) {
      setIsPolling(false);
      setTimedOut(true);
      setError("Processing is taking longer than expected. Please check back in history or try again.");
      return;
    }

    attemptsRef.current += 1;
    setAttemptCount(attemptsRef.current);

    try {
      const data = await getJobResult(jobId);
      setJob(data);
      setStatus(data.status);

      if (data.status === JobStatus.COMPLETED) {
        setIsPolling(false);
      } else if (data.status === JobStatus.FAILED) {
        setIsPolling(false);
        setError("Disaster analysis model failed to process this image.");
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`[HTTP ${err.status}] ${err.message}`);
      } else {
        setError("An unexpected error occurred while checking job status.");
      }
      setIsPolling(false);
    }
  }, [jobId]);

  useEffect(() => {
    if (!jobId) {
      setJob(null);
      setStatus(null);
      setIsPolling(false);
      setError(null);
      setAttemptCount(0);
      setTimedOut(false);
      attemptsRef.current = 0;
      return;
    }

    setIsPolling(true);
    setError(null);
    setTimedOut(false);
    attemptsRef.current = 0;

    // Immediate initial check
    poll();

    // Set up 2-second interval timer
    const timer = setInterval(() => {
      // Only continue polling if still active
      if (
        attemptsRef.current < MAX_POLL_ATTEMPTS &&
        status !== JobStatus.COMPLETED &&
        status !== JobStatus.FAILED
      ) {
        poll();
      }
    }, POLL_INTERVAL_MS);

    return () => clearInterval(timer);
  }, [jobId, poll, status]);

  const restartPolling = () => {
    attemptsRef.current = 0;
    setAttemptCount(0);
    setError(null);
    setTimedOut(false);
    if (jobId) {
      setIsPolling(true);
      poll();
    }
  };

  return {
    job,
    status,
    isPolling,
    error,
    attemptCount,
    timedOut,
    restartPolling,
  };
}
