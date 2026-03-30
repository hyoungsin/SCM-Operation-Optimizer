import { apiClient } from "../api/client";

export function DownloadPage({ run, onRestart }) {
  const downloadUrl = run.runId ? apiClient.downloadUrl(run.runId) : "#";

  return (
    <section className="panel">
      <h2>Download</h2>
      <div className="grid">
        <div className="row">
          <strong>Status</strong>
          <span>{run.solve?.status || "-"}</span>
        </div>
        <div className="row">
          <strong>Objective Value</strong>
          <span>{run.solve?.objective_value ?? "-"}</span>
        </div>
        <div className="row">
          <strong>Output File</strong>
          <span>{run.solve?.output_file || "-"}</span>
        </div>
      </div>
      <div className="actions">
        <a className="button" href={downloadUrl}>
          Download Output
        </a>
        <button className="button secondary" type="button" onClick={onRestart}>
          New Run
        </button>
      </div>
    </section>
  );
}
