import { useState } from "react";

export function UploadPanel({ state, onUpload }) {
  const [file, setFile] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      return;
    }
    await onUpload(file);
  }

  return (
    <section className="panel">
      <h2>Upload</h2>
      <p>Upload one SCM workbook. A new upload resets all downstream states.</p>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".xlsx"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
        />
        {state.uploadError && <p className="error-text">{state.uploadError}</p>}
        <div className="actions">
          <button className="button" type="submit" disabled={state.uploadLoading}>
            {state.uploadLoading ? "Uploading..." : "Upload Excel"}
          </button>
        </div>
      </form>
    </section>
  );
}
