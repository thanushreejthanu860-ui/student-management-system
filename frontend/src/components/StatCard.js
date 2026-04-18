export default function StatCard({ icon, label, value, color }) {
  return (
    <div className="stat-card" style={{ '--card-color': color }}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-info">
        <div className="stat-value">{value ?? '—'}</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  );
}
