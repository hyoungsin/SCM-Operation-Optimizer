import { useState } from "react";

export function UploadPage({ onUpload }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setError("Please select an .xlsx file.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      await onUpload(file);
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <h2>Upload</h2>
      <p>Upload one input workbook with the required SCM sheets.</p>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".xlsx"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
        />
        {error && <p>{error}</p>}
        <div className="actions">
          <button className="button" type="submit" disabled={loading}>
            {loading ? "Uploading..." : "Upload File"}
          </button>
        </div>
      </form>
    </section>
  );
}
