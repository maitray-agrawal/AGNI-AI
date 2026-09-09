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
