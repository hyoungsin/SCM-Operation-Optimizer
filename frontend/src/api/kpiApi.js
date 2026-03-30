import { getRunResult } from "./resultApi";

export async function getKpiSummary(runId) {
  const result = await getRunResult(runId);
  return result.kpi_summary;
}
