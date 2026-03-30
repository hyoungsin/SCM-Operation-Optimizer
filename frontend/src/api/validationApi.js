import { apiClient } from "./client";

export async function validateRun(runId) {
  return apiClient.request(`/runs/${runId}/validate`, {
    method: "POST",
  });
}

export function getValidationReportUrl(runId) {
  return `${apiClient.apiBaseUrl}/runs/${runId}/validation-report`;
}
