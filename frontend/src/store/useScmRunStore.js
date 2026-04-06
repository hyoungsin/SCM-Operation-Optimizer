import { create } from "zustand";

import { getCorrectedPreview } from "../api/previewApi";
import { getKpiSummary } from "../api/kpiApi";
import { getRunResult } from "../api/resultApi";
import { solveRun } from "../api/solveApi";
import { uploadItemDeliveryWorkbook, uploadPullInputWorkbook } from "../api/uploadApi";
import { validateRun } from "../api/validationApi";
import { createInitialRunState } from "../types/runState";

function deriveStatus(step, state) {
  if (step === "Upload") {
    return state.uploadStatus.pull_input_data_uploaded && state.uploadStatus.item_delivery_uploaded ? "complete" : "incomplete";
  }
  if (step === "Validation") {
    if (!state.uploadStatus.pull_input_data_uploaded || !state.uploadStatus.item_delivery_uploaded) return "incomplete";
    if (!state.validation) return "incomplete";
    return state.validation.solve_allowed ? "complete" : "error";
  }
  if (step === "Review") {
    if (!state.validation) return "incomplete";
    if (state.validation.solve_allowed === false) return "error";
    return state.preview ? "complete" : "incomplete";
  }
  if (step === "Solve") {
    if (!state.validation) return "incomplete";
    if (state.validation.solve_allowed === false) return "error";
    return state.solveSummary ? "complete" : "incomplete";
  }
  if (step === "Result") {
    if (!state.solveSummary) return "incomplete";
    return state.result ? "complete" : "incomplete";
  }
  if (step === "Report") {
    return state.result ? "complete" : "incomplete";
  }
  return "incomplete";
}

export const useScmRunStore = create((set, get) => ({
  ...createInitialRunState(),

  setActiveStep(step) {
    set({ activeStep: step });
  },

  resetForNewUpload() {
    set(createInitialRunState());
  },

  async uploadPullInput(file) {
    set({ uploadLoading: true, uploadError: "" });
    try {
      const uploaded = await uploadPullInputWorkbook(file);
      set({
        ...createInitialRunState(),
        runId: uploaded.run_id,
        displayRunId: uploaded.display_run_id,
        filename: uploaded.filename,
        pullInputFilename: uploaded.filename,
        uploadStatus: uploaded.upload_status,
        uploadTime: uploaded.upload_time,
        currentStatus: "pull_input_uploaded",
        activeStep: "Upload",
        uploadLoading: false,
      });
      return uploaded;
    } catch (error) {
      set({ uploadLoading: false, uploadError: error.message });
      throw error;
    }
  },

  async uploadItemDelivery(file) {
    const { runId, pullInputFilename } = get();
    if (!runId) {
      throw new Error("Please upload pull-input-data first.");
    }

    set({ uploadLoading: true, uploadError: "" });
    try {
      const uploaded = await uploadItemDeliveryWorkbook(runId, file);
      set({
        runId: uploaded.run_id,
        displayRunId: uploaded.display_run_id,
        filename: uploaded.filename,
        pullInputFilename,
        itemDeliveryFilename: file.name,
        uploadStatus: uploaded.upload_status,
        uploadTime: uploaded.upload_time,
        currentStatus: "uploaded",
        validation: null,
        validationError: "",
        preview: null,
        previewError: "",
        solveSummary: null,
        solveError: "",
        kpiSummary: null,
        kpiError: "",
        result: null,
        resultError: "",
        activeStep: "Validation",
        uploadLoading: false,
      });
      return uploaded;
    } catch (error) {
      set({ uploadLoading: false, uploadError: error.message });
      throw error;
    }
  },

  async validate() {
    const { runId, uploadStatus } = get();
    if (!runId) {
      throw new Error("Upload must be completed first.");
    }
    if (!uploadStatus.pull_input_data_uploaded || !uploadStatus.item_delivery_uploaded) {
      throw new Error("Both upload files must be completed before validation.");
    }

    set({ validationLoading: true, validationError: "" });
    try {
      const validation = await validateRun(runId);
      set({
        validation,
        currentStatus: validation.solve_allowed ? "validated" : "validation_error",
        activeStep: "Validation",
        validationLoading: false,
      });
      return validation;
    } catch (error) {
      set({ validationLoading: false, validationError: error.message });
      throw error;
    }
  },

  async loadPreview() {
    const { runId } = get();
    set({ previewLoading: true, previewError: "" });
    try {
      const preview = await getCorrectedPreview(runId);
      set({ preview, previewLoading: false, activeStep: "Review" });
      return preview;
    } catch (error) {
      set({ previewLoading: false, previewError: error.message });
      throw error;
    }
  },

  async solve() {
    const { runId } = get();
    set({ solveLoading: true, solveError: "" });
    try {
      const solveSummary = await solveRun(runId);
      set({
        solveSummary,
        currentStatus: solveSummary.solve_executed ? "solved" : "solve_failed",
        activeStep: "Solve",
        solveLoading: false,
      });
      return solveSummary;
    } catch (error) {
      set({ solveLoading: false, solveError: error.message });
      throw error;
    }
  },

  async loadResult() {
    const { runId } = get();
    set({ resultLoading: true, resultError: "", kpiLoading: true, kpiError: "" });
    try {
      const [result, kpiSummary] = await Promise.all([getRunResult(runId), getKpiSummary(runId)]);
      set({
        result,
        kpiSummary,
        resultLoading: false,
        kpiLoading: false,
        activeStep: "Result",
      });
      return result;
    } catch (error) {
      set({
        resultLoading: false,
        resultError: error.message,
        kpiLoading: false,
        kpiError: error.message,
      });
      throw error;
    }
  },

  getStepStatus(step) {
    return deriveStatus(step, get());
  },
}));
