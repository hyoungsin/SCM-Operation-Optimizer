export function StepNavigator({ activeStep, stepSequence, onStepClick, getStepStatus }) {
  return (
    <section className="wizard-stepper sticky">
      {stepSequence.map((step, index) => {
        const status = getStepStatus(step);
        const isActive = step === activeStep;

        return (
          <button
            type="button"
            key={step}
            className={[
              "wizard-step",
              isActive ? "active" : "",
              status === "complete" ? "completed" : "",
              status === "error" ? "warning" : "",
              status === "incomplete" ? "incomplete" : "",
            ]
              .filter(Boolean)
              .join(" ")}
            onClick={() => onStepClick(step)}
          >
            <span className="wizard-step-index">{index + 1}</span>
            <span>{step}</span>
          </button>
        );
      })}
    </section>
  );
}
