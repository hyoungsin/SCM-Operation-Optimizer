import { ReportPanel } from "../components/report/ReportPanel";
import { PreviewPanel } from "../components/preview/PreviewPanel";
import { ResultPanel } from "../components/result/ResultPanel";
import { SolvePanel } from "../components/solve/SolvePanel";
import { StepNavigator } from "../components/stepper/StepNavigator";
import { UploadPanel } from "../components/upload/UploadPanel";
import { ValidationPanel } from "../components/validation/ValidationPanel";
import { useScmRunStore } from "../store/useScmRunStore";
import { STEP_SEQUENCE } from "../types/runState";

export function ScmMilpWizardPage() {
  const state = useScmRunStore((store) => store);

  async function handleUpload(file) {
    await state.upload(file);
  }

  async function handleValidate() {
    await state.validate();
  }

  async function handleLoadPreview() {
    await state.loadPreview();
  }

  async function handleSolve() {
    await state.solve();
  }

  async function handleLoadResult() {
    await state.loadResult();
  }

  function renderStepPanel() {
    switch (state.activeStep) {
      case "Upload":
        return <UploadPanel state={state} onUpload={handleUpload} />;
      case "Validation":
        return <ValidationPanel state={state} onValidate={handleValidate} />;
      case "Review":
        return <PreviewPanel state={state} onLoadPreview={handleLoadPreview} enabled={Boolean(state.validation)} />;
      case "Solve":
        return <SolvePanel state={state} solveAllowed={Boolean(state.validation?.solve_allowed)} onSolve={handleSolve} />;
      case "Result":
        return <ResultPanel state={state} enabled={Boolean(state.solveSummary?.solve_executed)} onLoadResult={handleLoadResult} />;
      case "Report":
        return <ReportPanel state={state} resultReady={Boolean(state.solveSummary?.solve_executed)} />;
      default:
        return <UploadPanel state={state} onUpload={handleUpload} />;
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <h1>SCM Operation Optimizer</h1>
        <p>Run the process step by step and only focus on the essential summary values.</p>
      </section>

      <section className="panel run-summary">
        <h2>Run Summary</h2>
        <div className="grid summary-grid">
          <div className="metric-card">
            <span>Run ID</span>
            <strong>{state.runId || "-"}</strong>
          </div>
          <div className="metric-card">
            <span>File Name</span>
            <strong>{state.filename || "-"}</strong>
          </div>
          <div className="metric-card">
            <span>Status</span>
            <strong>{state.currentStatus}</strong>
          </div>
        </div>
      </section>

      <StepNavigator
        activeStep={state.activeStep}
        stepSequence={STEP_SEQUENCE}
        onStepClick={state.setActiveStep}
        getStepStatus={state.getStepStatus}
      />

      {renderStepPanel()}
    </main>
  );
}
