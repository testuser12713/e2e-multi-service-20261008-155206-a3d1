import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "../src/App";
import { apiBaseUrl } from "../src/api/client";
import type { Job } from "../src/api/client";

const jobs: Job[] = [
  {
    id: 2,
    text: "zweiter Auftrag",
    analysis: "word_count",
    status: "done",
    result: { word_count: 2 },
    error: null,
    created_at: "2025-03-14T09:41:08Z",
    updated_at: "2025-03-14T09:41:09Z",
  },
  {
    id: 1,
    text: "erster Auftrag",
    analysis: "reading_time",
    status: "pending",
    result: null,
    error: null,
    created_at: "2025-03-14T09:41:07Z",
    updated_at: "2025-03-14T09:41:07Z",
  },
];

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("App shell", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("renders the header and the live job count", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(jobs));
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    expect(
      screen.getByText("Auftragsverarbeitung"),
    ).toBeTruthy();
    expect(screen.getByRole("status").textContent).toContain("Aufträge im Store");

    await waitFor(() => {
      expect(screen.getByRole("status").textContent).toContain("2");
    });
  });

  it("fetches the job list from the contract /api/jobs path", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(jobs));
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled();
    });

    const [calledUrl, init] = fetchMock.mock.calls[0];
    expect(calledUrl).toBe(`${apiBaseUrl()}/api/jobs`);
    expect(init?.method ?? "GET").toBe("GET");

    await waitFor(() => {
      expect(screen.getByRole("status").textContent).toContain("2");
    });
  });

  it("starts with an empty store and reports the API as reachable", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([]));
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByRole("status").textContent).toContain("0");
    });
    expect(screen.getByTitle("API verbunden")).toBeTruthy();
  });

  it("shows the API as unreachable when the fetch fails", async () => {
    const fetchMock = vi.fn().mockRejectedValue(new Error("network down"));
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByTitle("API nicht erreichbar")).toBeTruthy();
    });
  });
});
