import { apiClient } from "./client";

export async function getCorrectedPreview(runId) {
  return apiClient.request(`/runs/${runId}/corrected-preview`);
}

export function getCorrectedPreviewFileUrl(runId) {
  return `${apiClient.apiBaseUrl}/runs/${runId}/corrected-preview-file`;
}
