import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AgentList } from "@/components/agent-console/agent-list";
import type { AgentRun } from "@/lib/types";

const mockRun: AgentRun = {
  id: "550e8400-e29b-41d4-a716-446655440000",
  task: "Fix the login bug",
  task_type: "bugfix",
  complexity: "moderate",
  status: "completed",
  total_tokens: 3200,
  total_cost: 0.0012,
  duration_ms: 18300,
  created_at: "2026-01-01T00:00:00Z",
  completed_at: "2026-01-01T00:00:18Z",
};

describe("AgentList", () => {
  it("shows empty state when no runs", () => {
    render(<AgentList runs={[]} />);
    expect(screen.getByText(/No agent runs yet/)).toBeInTheDocument();
  });

  it("renders run task name", () => {
    render(<AgentList runs={[mockRun]} />);
    expect(screen.getByText("Fix the login bug")).toBeInTheDocument();
  });

  it("renders status badge", () => {
    render(<AgentList runs={[mockRun]} />);
    expect(screen.getByText("completed")).toBeInTheDocument();
  });

  it("renders token count", () => {
    render(<AgentList runs={[mockRun]} />);
    expect(screen.getByText(/3200 tokens/)).toBeInTheDocument();
  });
});
