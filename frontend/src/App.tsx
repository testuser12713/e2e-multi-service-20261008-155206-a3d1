import { useCallback } from "react";
import { JobForm } from "./components/JobForm";
import { JobList } from "./components/JobList";
import { useJobs } from "./state/useJobs";
import type { CreateJobInput } from "./api/client";

export default function App() {
  const { jobs, loading, error, refresh, createJob } = useJobs();

  const handleSubmit = useCallback(
    async (input: CreateJobInput): Promise<void> => {
      try {
        await createJob(input);
      } catch {
        // The store already exposes the error for the UI to render.
      }
    },
    [createJob],
  );

  const apiReachable = error === null;

  return (
    <div className="app">
      <header className="app-header">
        <div className="container app-header__inner">
          <div className="app-header__brand">
            <span className="app-header__accent" aria-hidden="true" />
            <span className="app-header__title">Auftragsverarbeitung</span>
          </div>
          <div
            className="app-header__status"
            data-state={apiReachable ? "up" : "down"}
            title={apiReachable ? "API verbunden" : "API nicht erreichbar"}
          >
            <span className="app-header__dot" aria-hidden="true" />
            <span className="app-header__status-text">
              {apiReachable ? "API verbunden" : "API nicht erreichbar"}
            </span>
          </div>
        </div>
      </header>

      <main className="container app-main">
        <p className="live-count" role="status">
          Aufträge im Store:{" "}
          <span className="live-count__value">{jobs.length}</span>
        </p>
        <div className="app-columns">
          <section className="app-column app-column--form">
            <JobForm onSubmit={handleSubmit} />
          </section>
          <section className="app-column app-column--list">
            <JobList
              jobs={jobs}
              loading={loading}
              error={error}
              onRefresh={() => void refresh()}
            />
          </section>
        </div>
      </main>
    </div>
  );
}
