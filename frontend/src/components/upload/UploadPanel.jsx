import { useState } from "react";

export function UploadPanel({ state, onUploadPullInput, onUploadItemDelivery }) {
  const [pullInputFile, setPullInputFile] = useState(null);
  const [itemDeliveryFile, setItemDeliveryFile] = useState(null);

  const pullUploaded = Boolean(state.uploadStatus?.pull_input_data_uploaded);
  const itemUploaded = Boolean(state.uploadStatus?.item_delivery_uploaded);
  const pullUploading = state.uploadLoading && state.uploadLoadingType === "pull";
  const itemUploading = state.uploadLoading && state.uploadLoadingType === "item";

  async function handlePullInputSubmit(event) {
    event.preventDefault();
    if (!pullInputFile) {
      return;
    }
    await onUploadPullInput(pullInputFile);
  }

  async function handleItemDeliverySubmit(event) {
    event.preventDefault();
    if (!itemDeliveryFile) {
      return;
    }
    await onUploadItemDelivery(itemDeliveryFile);
  }

  return (
    <section className="panel">
      <h2>Upload</h2>
      <p>VS-OLAP Data에 이슈자재의 공급계획을 추가로 upload해주세요.</p>
      <div className="grid summary-grid">
        <div className="metric-card">
          <span>VS-OLAP(Batch)</span>
          <strong>{state.pullInputFilename || "No File"}</strong>
        </div>
        <div className="metric-card">
          <span>Item Delivery Plan (Upload)</span>
          <strong>{state.itemDeliveryFilename || "No File"}</strong>
        </div>
      </div>

      <div className="upload-grid">
        <form className="upload-box" onSubmit={handlePullInputSubmit}>
          <h3>1. VS-OLAP(Batch)</h3>
          <input
            type="file"
            accept=".xlsx"
            onChange={(event) => setPullInputFile(event.target.files?.[0] || null)}
          />
          <div className="actions">
            <button
              className={`button${pullUploaded ? " secondary" : ""}`}
              type="submit"
              disabled={state.uploadLoading}
            >
              {pullUploading ? "Uploading..." : "Upload VS-OLAP(Batch)"}
            </button>
          </div>
        </form>

        <form className="upload-box" onSubmit={handleItemDeliverySubmit}>
          <h3>2. Item Delivery Plan (Upload)</h3>
          <input
            type="file"
            accept=".xlsx"
            disabled={!state.runId || state.uploadLoading}
            onChange={(event) => setItemDeliveryFile(event.target.files?.[0] || null)}
          />
          <div className="actions">
            <button
              className={`button${itemUploaded ? " secondary" : ""}`}
              type="submit"
              disabled={!state.runId || state.uploadLoading}
            >
              {itemUploading ? "Uploading..." : "Upload Item Delivery Plan (Upload)"}
            </button>
          </div>
        </form>
      </div>

      {state.uploadError && <p className="error-text">{state.uploadError}</p>}
    </section>
  );
}
