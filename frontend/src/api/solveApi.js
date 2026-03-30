import { apiClient } from "./client";

export async function solveRun(runId) {
  return apiClient.request(`/runs/${runId}/solve`, {
    method: "POST",
  });
}
