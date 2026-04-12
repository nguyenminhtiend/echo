export interface AgentRun {
  id: string;
  task: string;
  task_type: string | null;
  complexity: string | null;
  status: string;
  total_tokens: number;
  total_cost: number;
  duration_ms: number | null;
  created_at: string;
  completed_at: string | null;
}

export interface AgentRunList {
  runs: AgentRun[];
  total: number;
}

export interface TraceEventRest {
  id: string;
  run_id: string;
  event_type: string;
  agent_name: string | null;
  data: Record<string, unknown>;
  tokens_in: number | null;
  tokens_out: number | null;
  cost: string | null;
  duration_ms: number | null;
  created_at: string;
}

export interface TraceTreeResponse {
  run_id: string;
  events: TraceEventRest[];
}

export interface RAGResult {
  content: string;
  chunk_type: string | null;
  file_path: string | null;
  start_line: number | null;
  end_line: number | null;
  score: number;
}

export interface RAGQueryResponse {
  results: RAGResult[];
  query: string;
}
