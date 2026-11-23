import './StatCard.css'

function StatCard({ title, value, description, color }) {
  return (
    <div className="stat-card">
      <div className="stat-card-header">
        <span>{title}</span>
      </div>

      <h2 style={{ color: color }}>{value}</h2>

      <p>{description}</p>
    </div>
  )
}

export default StatCard