export interface VerificationCheck {
  name: string;
  passed: boolean;
  details?: string;
}

export interface VerificationResult {
  status: 'passed' | 'failed';
  checks: VerificationCheck[];
}

export interface OutputDeliverable {
  type: string;
  filename: string;
  path: string;
  size_bytes: number;
}

export interface TraceEvent {
  step: string;
  timestamp: string;
  duration_ms: number;
  status: string;
  details?: Record<string, any>;
}

export interface PlanStep {
  step_id: number;
  name: string;
  description: string;
}

export interface TaskRunResponse {
  task_id: string;
  status: string;
  selected_model?: string;
  plan: PlanStep[];
  summary: string;
  verification?: VerificationResult;
  outputs: OutputDeliverable[];
  trace_summary: TraceEvent[];
}

export interface ModelInfo {
  id: string;
  name: string;
  role?: string;
  capabilities: string[];
  status: string;
}

export interface SecurityStatus {
  air_gapped: boolean;
  inference_runtime: string;
  inference_endpoint: string;
  vector_db: string;
  active_sockets: Array<{
    pid: number;
    local_address: string;
    remote_address: string;
    status: string;
    is_loopback: boolean;
  }>;
  external_ai_api_calls: number;
  external_network_connections: number;
  sandbox_network_isolated: boolean;
}
