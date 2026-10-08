import type { Job } from "../api/client";

export interface JobListProps {
  jobs: Job[];
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}

/**
 * Placeholder for the job list. Final prop contract only; the rows, status
 * labels and refresh control are built by the ticket that owns the list.
 */
export function JobList(_props: JobListProps) {
  return <></>;
}
