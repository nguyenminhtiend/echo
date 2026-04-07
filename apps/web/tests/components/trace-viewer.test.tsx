import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TraceTree } from "@/components/trace-viewer/trace-tree";
import { TraceNode } from "@/components/trace-viewer/trace-node";
import type { TraceEvent } from "@/lib/ws-client";

const mockEvent: TraceEvent = {
  type: "agent_start",
  agent_name: "coder",
  data: { task: "fix bug" },
  duration_ms: 1200,
  tokens_in: 100,
  tokens_out: 50,
  cost: 0.001,
  created_at: "2026-01-01T00:00:00Z",
};

describe("TraceNode", () => {
  it("renders event type badge", () => {
    render(<TraceNode event={mockEvent} />);
    expect(screen.getByText("agent_start")).toBeInTheDocument();
  });

  it("renders agent name", () => {
    render(<TraceNode event={mockEvent} />);
    expect(screen.getByText("coder")).toBeInTheDocument();
  });

  it("renders duration", () => {
    render(<TraceNode event={mockEvent} />);
    expect(screen.getByText("1200ms")).toBeInTheDocument();
  });

  it("renders token counts", () => {
    render(<TraceNode event={mockEvent} />);
    expect(screen.getByText("100 tok in")).toBeInTheDocument();
    expect(screen.getByText("50 tok out")).toBeInTheDocument();
  });
});

describe("TraceTree", () => {
  it("shows waiting message when no events", () => {
    render(<TraceTree events={[]} />);
    expect(screen.getByText("Waiting for trace events...")).toBeInTheDocument();
  });

  it("renders events when provided", () => {
    render(<TraceTree events={[mockEvent]} />);
    expect(screen.getByText("agent_start")).toBeInTheDocument();
  });
});
