import { getValidationReportUrl } from "../../api/validationApi";
import { formatNumber } from "../../types/runState";

export function ValidationPanel({ state, onValidate, onLoadPreview }) {
  const validation = state.validation;
  const uploadReady = state.uploadStatus?.pull_input_data_uploaded && state.uploadStatus?.item_delivery_uploaded;
  const reviewEnabled = Boolean(validation?.solve_allowed);

  return (
    <section className="panel">
      <h2>Validation</h2>
      <p>전처리 이슈 대상 report 조회 단계입니다. 두 개의 입력 파일 업로드 완료 후 검증을 실행할 수 있습니다.</p>
      <div className="actions">
        <button className="button" type="button" onClick={onValidate} disabled={!uploadReady || state.validationLoading}>
          {state.validationLoading ? "Validating..." : validation ? "Re-run Validation" : "Run Validation"}
        </button>
        {validation && (
          <a className="button secondary" href={getValidationReportUrl(state.runId)}>
            Download Validation Issue Report
          </a>
        )}
        {validation && (
          <button className="button next-step" type="button" onClick={onLoadPreview} disabled={!reviewEnabled || state.previewLoading}>
            Load Review
          </button>
        )}
      </div>
      {!uploadReady && <p className="error-text">pull-input-data와 item-delivery update 업로드를 모두 완료해 주세요.</p>}
      {state.validationError && <p className="error-text">{state.validationError}</p>}
      {validation && (
        <div className="grid summary-grid">
          <div className="metric-card">
            <span>Validation Status</span>
            <strong>{validation.validation_status}</strong>
          </div>
          <div className="metric-card">
            <span>Error Count</span>
            <strong>{formatNumber(validation.summary.errors)}</strong>
          </div>
          <div className="metric-card">
            <span>Warning Count</span>
            <strong>{formatNumber(validation.summary.warnings)}</strong>
          </div>
          <div className="metric-card">
            <span>Solve Allowed</span>
            <strong>{validation.solve_allowed ? "Yes" : "No"}</strong>
          </div>
        </div>
      )}
    </section>
  );
}
