export type Analysis = "word_count" | "top_words" | "reading_time";

export type JobStatus = "pending" | "in_progress" | "done" | "failed";

export interface Job {
  id: number;
  text: string;
  analysis: Analysis;
  status: JobStatus;
  result: Record<string, unknown> | null;
  error: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateJobInput {
  text: string;
  analysis: Analysis;
}

const DEFAULT_API_BASE_URL = "http://localhost:8000";

/**
 * Base URL of the jobs API. Configured via VITE_API_BASE_URL, falling back to
 * the contract default. A trailing slash is stripped so paths join cleanly.
 */
export function apiBaseUrl(): string {
  const configured = import.meta.env.VITE_API_BASE_URL;
  const base =
    typeof configured === "string" && configured.length > 0
      ? configured
      : DEFAULT_API_BASE_URL;
  return base.replace(/\/+$/, "");
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    throw new Error("API nicht erreichbar");
  }

  if (!response.ok) {
    throw new Error(await readErrorDetail(response));
  }

  return (await response.json()) as T;
}

async function readErrorDetail(response: Response): Promise<string> {
  try {
    const body: unknown = await response.json();
    if (
      body !== null &&
      typeof body === "object" &&
      "detail" in body &&
      typeof (body as { detail: unknown }).detail === "string"
    ) {
      return (body as { detail: string }).detail;
    }
  } catch {
    // Non-JSON error body: fall through to the HTTP status.
  }
  return `HTTP ${response.status}`;
}

export function listJobs(): Promise<Job[]> {
  return request<Job[]>("/api/jobs");
}

export function getJob(id: number): Promise<Job> {
  return request<Job>(`/api/jobs/${id}`);
}

export function createJob(input: CreateJobInput): Promise<Job> {
  return request<Job>("/api/jobs", {
    method: "POST",
    body: JSON.stringify(input),
  });
}
