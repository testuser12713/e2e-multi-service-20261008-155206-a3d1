import { useCallback, useEffect, useState } from "react";
import {
  createJob as createJobRequest,
  listJobs,
  type CreateJobInput,
  type Job,
} from "../api/client";

export interface UseJobsResult {
  jobs: Job[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  createJob: (input: CreateJobInput) => Promise<void>;
}

function messageOf(cause: unknown): string {
  return cause instanceof Error ? cause.message : "Unbekannter Fehler";
}

/**
 * Shared job store: one list of jobs with loading/error state, a refresh that
 * fetches the list and a createJob that posts and then refreshes. There is
 * deliberately NO polling here — automatic refresh is a later ticket.
 */
export function useJobs(): UseJobsResult {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async (): Promise<void> => {
    setLoading(true);
    try {
      const next = await listJobs();
      setJobs(next);
      setError(null);
    } catch (cause) {
      setError(messageOf(cause));
    } finally {
      setLoading(false);
    }
  }, []);

  const createJob = useCallback(
    async (input: CreateJobInput): Promise<void> => {
      try {
        await createJobRequest(input);
      } catch (cause) {
        setError(messageOf(cause));
        throw cause;
      }
      await refresh();
    },
    [refresh],
  );

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { jobs, loading, error, refresh, createJob };
}
