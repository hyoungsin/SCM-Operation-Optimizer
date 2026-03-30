export function ValidationPage({ run, onValidate, onBack }) {
  const issues = run.validation?.issues || [];
  const canSolve = run.validation?.can_solve;

  return (
    <section className="panel">
      <h2>Validation</h2>
      <p>Run the initial workbook structure validation.</p>
      {run.validation ? (
        <>
          <div className="grid">
            <div className="row">
              <strong>Errors</strong>
              <span>{run.validation.summary.errors}</span>
            </div>
            <div className="row">
              <strong>Warnings</strong>
              <span>{run.validation.summary.warnings}</span>
            </div>
            <div className="row">
              <strong>Infos</strong>
              <span>{run.validation.summary.infos}</span>
            </div>
            <div className="row">
              <strong>Can Solve</strong>
              <span>{canSolve ? "Yes" : "No"}</span>
            </div>
          </div>
          <div className="actions">
            <button className="button secondary" type="button" onClick={onBack}>
              Back
            </button>
            <button className="button" type="button" onClick={onValidate}>
              Re-run Validation
            </button>
          </div>
          <div className="grid" style={{ marginTop: "16px" }}>
            {issues.map((issue, index) => (
              <div key={`${issue.sheet}-${index}`} className="issue">
                <strong>{issue.level.toUpperCase()}</strong> [{issue.sheet}] {issue.message}
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="actions">
          <button className="button secondary" type="button" onClick={onBack}>
            Back
          </button>
          <button className="button" type="button" onClick={onValidate}>
            Run Validation
          </button>
        </div>
      )}
    </section>
  );
}
