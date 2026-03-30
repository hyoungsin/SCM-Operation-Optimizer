import { apiClient } from "./client";

export async function uploadWorkbook(file) {
  const formData = new FormData();
  formData.append("file", file);

  return apiClient.request("/upload", {
    method: "POST",
    body: formData,
  });
}
