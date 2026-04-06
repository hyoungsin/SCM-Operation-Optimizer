import { useState } from "react";

export function UploadPanel({ state, onUploadPullInput, onUploadItemDelivery }) {
  const [pullInputFile, setPullInputFile] = useState(null);
  const [itemDeliveryFile, setItemDeliveryFile] = useState(null);

  const pullUploaded = Boolean(state.uploadStatus?.pull_input_data_uploaded);
  const itemUploaded = Boolean(state.uploadStatus?.item_delivery_uploaded);

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
          <span>VS-OLAP</span>
          <strong>{state.pullInputFilename || "No File"}</strong>
        </div>
        <div className="metric-card">
          <span>item delivery plan</span>
          <strong>{state.itemDeliveryFilename || "No File"}</strong>
        </div>
      </div>

      <div className="upload-grid">
        <form className="upload-box" onSubmit={handlePullInputSubmit}>
          <h3>1. VS-OLAP</h3>
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
              {state.uploadLoading ? "Uploading..." : "Upload VS-OLAP"}
            </button>
          </div>
        </form>

        <form className="upload-box" onSubmit={handleItemDeliverySubmit}>
          <h3>2. item delivery plan</h3>
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
              {state.uploadLoading ? "Uploading..." : "Upload item delivery plan"}
            </button>
          </div>
        </form>
      </div>

      {state.uploadError && <p className="error-text">{state.uploadError}</p>}
    </section>
  );
}
