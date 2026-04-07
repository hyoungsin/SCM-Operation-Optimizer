export function createInitialRunState() {
  return {
    activeStep: "Upload",
    runId: "",
    displayRunId: "",
    filename: "",
    pullInputFilename: "",
    itemDeliveryFilename: "",
    uploadStatus: {
      pull_input_data_uploaded: false,
      item_delivery_uploaded: false,
    },
    uploadTime: "",
    currentStatus: "idle",
    uploadLoading: false,
    uploadLoadingType: "",
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

export function getRunStatusLabel(state) {
  if (state.uploadLoading) {
    return "Uploading";
  }
  if (!state.uploadStatus?.pull_input_data_uploaded && !state.uploadStatus?.item_delivery_uploaded) {
    return "Upload";
  }
  if (state.activeStep && STEP_SEQUENCE.includes(state.activeStep)) {
    return state.activeStep;
  }
  return "Upload";
}

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

export function formatPercent(value, digits = 1) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  const number = Number(value);
  if (Number.isNaN(number)) {
    return String(value);
  }

  return `${(number * 100).toFixed(digits)}%`;
}

export function formatMillions(value) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  const number = Number(value);
  if (Number.isNaN(number)) {
    return String(value);
  }

  const millions = Math.round(number / 1_000_000);
  return `${new Intl.NumberFormat("en-US").format(millions)}M`;
}

export function formatOneDecimal(value) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  const number = Number(value);
  if (Number.isNaN(number)) {
    return String(value);
  }

  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(number);
}
