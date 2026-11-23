
import './SLAOverview.css'

function SLAOverview({ tickets = [] }) {

  const totalTickets = tickets.length

  const responseBreaches = tickets.filter(
    (ticket) => ticket.response_breached
  ).length

  const resolutionBreaches = tickets.filter(
    (ticket) => ticket.resolution_breached
  ).length

  const totalBreaches = tickets.filter(
    (ticket) =>
      ticket.response_breached || ticket.resolution_breached
  ).length

  const responseCompleted = tickets.filter(
    (ticket) => ticket.first_response_at !== null
  ).length

  const resolutionCompleted = tickets.filter(
    (ticket) => ticket.resolved_at !== null
  ).length

  const responseRate = totalTickets
    ? Math.round((responseCompleted / totalTickets) * 100)
    : 0

  const resolutionRate = totalTickets
    ? Math.round((resolutionCompleted / totalTickets) * 100)
    : 0

  return (
    <section className="sla-overview">

      <div className="sla-header">
        <div>
          <h2>SLA Overview</h2>
          <p>Monitor response and resolution performance.</p>
        </div>
      </div>

      <div className="sla-grid">

        <div className="sla-card">
          <span>Response Completion</span>
          <h3>{responseRate}%</h3>
          <p>{responseCompleted} of {totalTickets} tickets responded to</p>
        </div>

        <div className="sla-card">
          <span>Resolution Completion</span>
          <h3>{resolutionRate}%</h3>
          <p>{resolutionCompleted} of {totalTickets} tickets resolved</p>
        </div>

        <div className="sla-card">
          <span>Response Breaches</span>
          <h3 className="breach-number">{responseBreaches}</h3>
          <p>Response deadlines missed</p>
        </div>

        <div className="sla-card">
          <span>Resolution Breaches</span>
          <h3 className="breach-number">{resolutionBreaches}</h3>
          <p>Resolution deadlines missed</p>
        </div>

      </div>

      <div className="sla-total">
        Total tickets with at least one SLA breach: <strong>{totalBreaches}</strong>
      </div>

    </section>
  )
}

export default SLAOverview
