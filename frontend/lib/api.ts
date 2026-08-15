import {
  JobRead,
  JobListResponse,
  PaginatedJobs,
  ImageType,
  JobStatus,
  BackendErrorResponse,
} from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

/**
 * Custom API Error class for typed error handling across the application.
 */
export class ApiError extends Error {
  public status: number;
  public code?: string;

  constructor(status: number, message: string, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;

    // Restore prototype chain for instanceof checks
    Object.setPrototypeOf(this, ApiError.prototype);
  }
}

/**
 * Parses HTTP error response body to extract error message & error code.
 */
async function parseErrorResponse(res: Response): Promise<{ message: string; code?: string }> {
  try {
    const data: BackendErrorResponse = await res.json();
    if (typeof data.detail === "string") {
      return { message: data.detail };
    }
    if (data.detail && typeof data.detail === "object") {
      const detailObj = data.detail as { message?: string; code?: string };
      return {
        message: detailObj.message || `HTTP ${res.status} ${res.statusText}`,
        code: detailObj.code,
      };
    }
  } catch {
    // If response body is not JSON or cannot be parsed
  }
  return { message: `Request failed with status ${res.status}: ${res.statusText}` };
}

/**
 * Helper to fetch with retry-once-on-network-failure behavior (GET requests only).
 */
async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  retries = 1
): Promise<Response> {
  try {
    return await fetch(url, options);
  } catch (error) {
    if (retries > 0) {
      // Retry once after 300ms delay for network/connectivity errors
      await new Promise((resolve) => setTimeout(resolve, 300));
      return fetchWithRetry(url, options, retries - 1);
    }
    throw new ApiError(
      0,
      `Network failure connecting to backend: ${error instanceof Error ? error.message : String(error)}`,
      "NETWORK_ERROR"
    );
  }
}

/**
 * Upload a satellite image to the backend for background disaster analysis.
 * Endpoint: POST /upload
 */
export async function uploadImage(
  file: File,
  imageType: ImageType = ImageType.OTHER
): Promise<JobRead & { job_id: string }> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("image_type", imageType);

  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}/upload`, {
      method: "POST",
      body: formData,
    });
  } catch (error) {
    throw new ApiError(
      0,
      `Network error uploading image: ${error instanceof Error ? error.message : String(error)}`,
      "NETWORK_ERROR"
    );
  }

  if (!res.ok) {
    const { message, code } = await parseErrorResponse(res);
    throw new ApiError(res.status, message, code);
  }

  const job: JobRead = await res.json();
  // Provide job_id convenience field alongside backend JobRead id
  return {
    ...job,
    job_id: job.id,
  };
}

/**
 * Get job analysis status and result details.
 * Endpoint: GET /results/{job_id}
 */
export async function getJobResult(jobId: string): Promise<JobRead> {
  const res = await fetchWithRetry(`${API_BASE_URL}/results/${jobId}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });

  if (!res.ok) {
    const { message, code } = await parseErrorResponse(res);
    throw new ApiError(res.status, message, code);
  }

  return res.json();
}

/**
 * List all analysis jobs with pagination and optional status filter.
 * Endpoint: GET /jobs?skip=X&limit=Y&status=Z
 */
export async function listJobs(
  page = 1,
  pageSize = 20,
  status?: JobStatus
): Promise<PaginatedJobs> {
  const skip = Math.max(0, (page - 1) * pageSize);
  const limit = Math.max(1, pageSize);

  const queryParams = new URLSearchParams({
    skip: skip.toString(),
    limit: limit.toString(),
  });

  if (status) {
    queryParams.append("status", status);
  }

  const res = await fetchWithRetry(`${API_BASE_URL}/jobs?${queryParams.toString()}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });

  if (!res.ok) {
    const { message, code } = await parseErrorResponse(res);
    throw new ApiError(res.status, message, code);
  }

  const data: JobListResponse = await res.json();
  return data;
}
