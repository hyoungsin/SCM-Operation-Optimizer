import { getCorrectedPreviewFileUrl } from "../../api/previewApi";
import { formatNumber } from "../../types/runState";

export function PreviewPanel({ state, onLoadPreview, onSolve, enabled }) {
  const preview = state.preview;
  const solveEnabled = Boolean(preview?.preview_generated && state.validation?.solve_allowed);

  return (
    <section className="panel">
      <h2>Review</h2>
      <p>전처리 dataset 조회 단계입니다. 보정된 dataset 요약을 확인하고 엑셀로 내려받을 수 있습니다.</p>
      <div className="actions">
        <button className="button" type="button" onClick={onLoadPreview} disabled={!enabled || state.previewLoading}>
          {state.previewLoading ? "Loading Review..." : preview ? "Refresh Review" : "Load Review"}
        </button>
        {preview && (
          <a className="button secondary" href={getCorrectedPreviewFileUrl(state.runId)}>
            Download Corrected Dataset
          </a>
        )}
        {preview && (
          <button className="button next-step" type="button" onClick={onSolve} disabled={!solveEnabled || state.solveLoading}>
            {state.solveLoading ? "Solving..." : "Solve 실행"}
          </button>
        )}
      </div>
      {state.previewError && <p className="error-text">{state.previewError}</p>}
      {preview && (
        <div className="grid summary-grid">
          <div className="metric-card">
            <span>Preview Generated</span>
            <strong>{preview.preview_generated ? "Yes" : "No"}</strong>
          </div>
          <div className="metric-card">
            <span>Sheets</span>
            <strong>{formatNumber(preview.sheets?.length || 0)}</strong>
          </div>
          <div className="metric-card">
            <span>Total Preview Rows</span>
            <strong>
              {formatNumber((preview.sheets || []).reduce((sum, sheet) => sum + (sheet.row_count || 0), 0))}
            </strong>
          </div>
        </div>
      )}
    </section>
  );
}
