/**
 * Enums matching backend app.models.enums
 */
export enum ImageType {
  IR = "IR",
  THERMAL = "THERMAL",
  OPTICAL = "OPTICAL",
  OTHER = "OTHER",
}

export enum JobStatus {
  PENDING = "PENDING",
  PROCESSING = "PROCESSING",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED",
}

export enum SeverityLevel {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

/**
 * Disaster Analysis Result matching backend ResultRead schema
 */
export interface ResultRead {
  id: string;
  job_id: string;
  disaster_type: string;
  severity: SeverityLevel;
  affected_area_estimate?: string | null;
  description?: string | null;
  confidence_score?: number | null;
  latitude?: number | null;
  longitude?: number | null;
  raw_model_output?: Record<string, unknown> | null;
  created_at: string;
}

// Alias for JobResult
export type JobResult = ResultRead;

/**
 * Job record matching backend JobRead schema
 */
export interface JobRead {
  id: string;
  image_url: string;
  image_type: ImageType;
  status: JobStatus;
  created_at: string;
  updated_at: string;
  result?: ResultRead | null;
}

/**
 * Paginated jobs list response matching backend JobListResponse schema
 */
export interface JobListResponse {
  total: number;
  skip: number;
  limit: number;
  jobs: JobRead[];
}

// Alias for PaginatedJobs
export type PaginatedJobs = JobListResponse;

/**
 * Error detail structures matching backend ErrorResponse
 */
export interface ErrorDetail {
  code?: string;
  message: string;
}

export interface BackendErrorResponse {
  detail: string | ErrorDetail | { [key: string]: unknown };
}
