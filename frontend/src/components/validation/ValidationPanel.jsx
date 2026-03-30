import { getValidationReportUrl } from "../../api/validationApi";
import { formatNumber } from "../../types/runState";

export function ValidationPanel({ state, onValidate }) {
  const validation = state.validation;

  return (
    <section className="panel">
      <h2>Validation</h2>
      <p>전처리 이슈 대상 report 조회 단계입니다. 검증 실행 후 이슈 리포트를 다운로드할 수 있습니다.</p>
      <div className="actions">
        <button className="button" type="button" onClick={onValidate} disabled={state.validationLoading}>
          {state.validationLoading ? "Validating..." : validation ? "Re-run Validation" : "Run Validation"}
        </button>
        {validation && (
          <a className="button secondary" href={getValidationReportUrl(state.runId)}>
            Download Validation Issue Report
          </a>
        )}
      </div>
      {state.validationError && <p className="error-text">{state.validationError}</p>}
      {validation && (
        <>
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
        </>
      )}
    </section>
  );
}
