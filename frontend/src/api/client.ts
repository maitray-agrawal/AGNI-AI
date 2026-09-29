import { TaskRunResponse, ModelInfo, SecurityStatus } from '../types';

const API_BASE = '/api';

export async function fetchHealth(): Promise<any> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchModels(): Promise<{ provider: string; endpoint: string; models: ModelInfo[] }> {
  const res = await fetch(`${API_BASE}/models`);
  if (!res.ok) throw new Error('Failed to load models');
  return res.json();
}

export async function fetchSecurityStatus(): Promise<SecurityStatus> {
  const res = await fetch(`${API_BASE}/security/status`);
  if (!res.ok) throw new Error('Failed to load security status');
  return res.json();
}

export async function submitTask(task: string, files: string[] = []): Promise<TaskRunResponse> {
  const res = await fetch(`${API_BASE}/tasks/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task, files, stream: false }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Task execution failed' }));
    throw new Error(err.detail || 'Failed to execute task');
  }
  return res.json();
}

export async function uploadDocument(file: File): Promise<{ filename: string; saved_path: string; size_bytes: number }> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/files/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('File upload failed');
  return res.json();
}

export function getDeliverableDownloadUrl(filename: string): string {
  return `${API_BASE}/outputs/${encodeURIComponent(filename)}`;
}

// ── Research Intelligence APIs ──────────────────────────────────────
export async function fetchSignals(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/signals`);
  if (!res.ok) throw new Error('Failed to load risk signals');
  return res.json();
}

export async function fetchEvents(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/events`);
  if (!res.ok) throw new Error('Failed to load events');
  return res.json();
}

export async function createManualEvent(eventData: any): Promise<any> {
  const res = await fetch(`${API_BASE}/events`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(eventData),
  });
  if (!res.ok) throw new Error('Failed to create manual event');
  return res.json();
}

export async function fetchRegimes(): Promise<any> {
  const res = await fetch(`${API_BASE}/regimes`);
  if (!res.ok) throw new Error('Failed to load regimes');
  return res.json();
}

export async function fetchScenarios(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/scenarios`);
  if (!res.ok) throw new Error('Failed to load scenarios');
  return res.json();
}

export async function runScenario(scenarioId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/scenarios/${scenarioId}/run`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to run scenario');
  return res.json();
}

export async function fetchGraph(): Promise<any> {
  const res = await fetch(`${API_BASE}/graph`);
  if (!res.ok) throw new Error('Failed to load risk graph');
  return res.json();
}

export async function fetchResearchSummary(): Promise<any> {
  const res = await fetch(`${API_BASE}/research/summary`);
  if (!res.ok) throw new Error('Failed to load research summary');
  return res.json();
}
