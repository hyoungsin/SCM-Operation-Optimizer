import { formatNumber } from "../../types/runState";

export function ResultPanel({ state, enabled, onLoadResult }) {
  const result = state.result;
  const kpi = state.kpiSummary;

  return (
    <section className="panel">
      <h2>Result</h2>
      <p>결과 요약 조회 단계입니다. 화면에는 핵심 KPI만 표시하고 상세 테이블은 노출하지 않습니다.</p>
      <div className="actions">
        <button className="button" type="button" onClick={onLoadResult} disabled={!enabled || state.resultLoading}>
          {state.resultLoading ? "Loading Result..." : result ? "결과 다시 조회" : "결과 조회"}
        </button>
      </div>
      {state.resultError && <p className="error-text">{state.resultError}</p>}
      {(result || kpi) && (
        <div className="grid summary-grid">
          <div className="metric-card">
            <span>Objective</span>
            <strong>{formatNumber(result?.objective_value)}</strong>
          </div>
          <div className="metric-card">
            <span>Total Shortage</span>
            <strong>{formatNumber(kpi?.total_shortage)}</strong>
          </div>
          <div className="metric-card">
            <span>Total Air Shipment</span>
            <strong>{formatNumber(kpi?.total_air_shipment)}</strong>
          </div>
          <div className="metric-card">
            <span>Total Air Cost</span>
            <strong>{formatNumber(kpi?.total_air_cost)}</strong>
          </div>
        </div>
      )}
    </section>
  );
}
