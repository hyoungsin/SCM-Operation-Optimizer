import { ReportPanel } from "../components/report/ReportPanel";
import { PreviewPanel } from "../components/preview/PreviewPanel";
import { ResultPanel } from "../components/result/ResultPanel";
import { SolvePanel } from "../components/solve/SolvePanel";
import { StepNavigator } from "../components/stepper/StepNavigator";
import { UploadPanel } from "../components/upload/UploadPanel";
import { ValidationPanel } from "../components/validation/ValidationPanel";
import { useScmRunStore } from "../store/useScmRunStore";
import { getRunStatusLabel, STEP_SEQUENCE } from "../types/runState";

export function ScmMilpWizardPage() {
  const state = useScmRunStore((store) => store);

  async function handleUploadPullInput(file) {
    await state.uploadPullInput(file);
  }

  async function handleUploadItemDelivery(file) {
    await state.uploadItemDelivery(file);
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

  function handleReset() {
    state.resetForNewUpload();
  }

  function handleMoveToReport() {
    state.setActiveStep("Report");
  }

  function renderStepPanel() {
    switch (state.activeStep) {
      case "Upload":
        return (
          <UploadPanel
            state={state}
            onUploadPullInput={handleUploadPullInput}
            onUploadItemDelivery={handleUploadItemDelivery}
          />
        );
      case "Validation":
        return <ValidationPanel state={state} onValidate={handleValidate} onLoadPreview={handleLoadPreview} />;
      case "Review":
        return <PreviewPanel state={state} onLoadPreview={handleLoadPreview} onSolve={handleSolve} enabled={Boolean(state.validation)} />;
      case "Solve":
        return (
          <SolvePanel
            state={state}
            solveAllowed={Boolean(state.validation?.solve_allowed)}
            onSolve={handleSolve}
            onLoadResult={handleLoadResult}
          />
        );
      case "Result":
        return (
          <ResultPanel
            state={state}
            enabled={Boolean(state.solveSummary?.solve_executed)}
            onLoadResult={handleLoadResult}
            onMoveToReport={handleMoveToReport}
          />
        );
      case "Report":
        return <ReportPanel state={state} resultReady={Boolean(state.result)} />;
      default:
        return (
          <UploadPanel
            state={state}
            onUploadPullInput={handleUploadPullInput}
            onUploadItemDelivery={handleUploadItemDelivery}
          />
        );
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <h1>SCM Operation Optimizer</h1>
        <p>단계별로 실행하면서 핵심 요약 값만 확인하세요.</p>
      </section>

      <section className="panel run-summary">
        <div className="panel-header">
          <h2>Run Summary</h2>
          <button className="button secondary" type="button" onClick={handleReset}>
            Clear
          </button>
        </div>
        <div className="grid summary-grid">
          <div className="metric-card">
            <span>Run ID</span>
            <strong>{state.displayRunId || "-"}</strong>
          </div>
          <div className="metric-card">
            <span>Status</span>
            <strong>{getRunStatusLabel(state)}</strong>
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
