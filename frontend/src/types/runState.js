export function createInitialRunState() {
  return {
    activeStep: "Upload",
    runId: "",
    filename: "",
    uploadTime: "",
    currentStatus: "idle",
    uploadLoading: false,
    uploadError: "",
    validation: null,
    validationLoading: false,
    validationError: "",
    preview: null,
    previewLoading: false,
    previewError: "",
    solveSummary: null,
    solveLoading: false,
    solveError: "",
    kpiSummary: null,
    kpiLoading: false,
    kpiError: "",
    result: null,
    resultLoading: false,
    resultError: "",
  };
}

export const STEP_SEQUENCE = ["Upload", "Validation", "Review", "Solve", "Result", "Report"];

export function formatNumber(value) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  const number = Number(value);
  if (Number.isNaN(number)) {
    return String(value);
  }

  return new Intl.NumberFormat("en-US").format(number);
}
