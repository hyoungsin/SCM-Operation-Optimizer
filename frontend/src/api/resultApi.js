import { apiClient } from "./client";

export async function getRunResult(runId) {
  return apiClient.request(`/runs/${runId}/result`);
}

export function getOutputFileUrl(runId) {
  return `${apiClient.apiBaseUrl}/runs/${runId}/output-file`;
}
