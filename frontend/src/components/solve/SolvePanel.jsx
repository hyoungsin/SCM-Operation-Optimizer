import { formatMillions } from "../../types/runState";

export function SolvePanel({ state, solveAllowed, onSolve, onLoadResult }) {
  return (
    <section className="panel">
      <h2>Solve</h2>
      <p>최적화 실행 단계입니다. Validation이 완료되어야만 실행할 수 있습니다.</p>
      <div className="grid">
        <div className="row">
          <strong>Run ID</strong>
          <span>{state.displayRunId || "-"}</span>
        </div>
        <div className="row">
          <strong>Validation Gate</strong>
          <span>{solveAllowed ? "Passed" : "Blocked"}</span>
        </div>
      </div>
      <div className="actions">
        <button className="button" type="button" onClick={onSolve} disabled={!solveAllowed || state.solveLoading}>
          {state.solveLoading ? "Solving..." : "Solve 실행"}
        </button>
        {state.solveSummary && (
          <button className="button next-step" type="button" onClick={onLoadResult} disabled={state.resultLoading}>
            {state.resultLoading ? "Loading Result..." : "결과 조회"}
          </button>
        )}
      </div>
      {state.solveError && <p className="error-text">{state.solveError}</p>}
      {state.solveSummary && (
        <div className="grid summary-grid">
          <div className="metric-card">
            <span>Status</span>
            <strong>{state.solveSummary.solve_status}</strong>
          </div>
          <div className="metric-card">
            <span>Termination</span>
            <strong>{state.solveSummary.termination_condition}</strong>
          </div>
          <div className="metric-card">
            <span>Objective</span>
            <strong>{formatMillions(state.solveSummary.objective_value)}</strong>
          </div>
          <div className="metric-card">
            <span>Time</span>
            <strong>{state.solveSummary.solving_time}s</strong>
          </div>
        </div>
      )}
    </section>
  );
}
