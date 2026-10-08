import type { CreateJobInput } from "../api/client";

export interface JobFormProps {
  onSubmit: (input: CreateJobInput) => Promise<void>;
}

/**
 * Placeholder for the job submission form. Final prop contract only; the
 * fields and validation are built by the ticket that owns the form.
 */
export function JobForm(_props: JobFormProps) {
  return <></>;
}
