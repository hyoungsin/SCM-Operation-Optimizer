export function Stepper({ steps, activeStep }) {
  return (
    <section className="stepper">
      {steps.map((step, index) => (
        <div key={step} className={`step ${index === activeStep ? "active" : ""}`}>
          {index + 1}. {step}
        </div>
      ))}
    </section>
  );
}
