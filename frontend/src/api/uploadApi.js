import { apiClient } from "./client";

export async function uploadPullInputWorkbook(file) {
  const formData = new FormData();
  formData.append("file", file);

  return apiClient.request("/upload/pull-input-data", {
    method: "POST",
    body: formData,
  });
}

export async function uploadItemDeliveryWorkbook(runId, file) {
  const formData = new FormData();
  formData.append("file", file);

  return apiClient.request(`/runs/${runId}/upload/item-delivery`, {
    method: "POST",
    body: formData,
  });
}
