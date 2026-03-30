export function StatusCard({ title, rows }) {
  return (
    <section className="panel">
      <h2>{title}</h2>
      <div className="grid">
        {rows.map((row) => (
          <div key={row.label} className="row">
            <strong>{row.label}</strong>
            <span>{row.value}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
