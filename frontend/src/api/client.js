const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    // Read the body only once; parsing failures must not re-read the stream.
    const raw = await response.text().catch(() => "");
    let detail = raw || "Request failed";
    try {
      const parsed = raw ? JSON.parse(raw) : null;
      if (parsed && typeof parsed === "object") {
        detail = parsed.detail || JSON.stringify(parsed);
      }
    } catch {
      // keep detail as raw text
    }
    throw new Error(detail);
  }

  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
  return response;
}

export const apiClient = {
  request,
  apiBaseUrl: API_BASE_URL,
};
