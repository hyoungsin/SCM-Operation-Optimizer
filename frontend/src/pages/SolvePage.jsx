export function SolvePage({ run, onSolve, onBack }) {
  const canSolve = run.validation?.can_solve;

  return (
    <section className="panel">
      <h2>Solve</h2>
      <p>Placeholder solve flow using FastAPI and a HiGHS placeholder runner.</p>
      <div className="grid">
        <div className="row">
          <strong>Run ID</strong>
          <span>{run.runId}</span>
        </div>
        <div className="row">
          <strong>Solver</strong>
          <span>HiGHS placeholder</span>
        </div>
        <div className="row">
          <strong>Validation Gate</strong>
          <span>{canSolve ? "Passed" : "Blocked"}</span>
        </div>
      </div>
      <div className="actions">
        <button className="button secondary" type="button" onClick={onBack}>
          Back
        </button>
        <button className="button" type="button" onClick={onSolve} disabled={!canSolve}>
          Run Solve
        </button>
      </div>
    </section>
  );
}
