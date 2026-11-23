
import './RecentTickets.css'

function RecentTickets() {
  const tickets = [
    {
      id: 'TKT-001',
      title: 'Office network connection failure',
      priority: 'High',
      status: 'Open'
    },
    {
      id: 'TKT-002',
      title: 'Printer connection issue',
      priority: 'High',
      status: 'In Progress'
    },
    {
      id: 'TKT-003',
      title: 'SLA first response test',
      priority: 'Critical',
      status: 'Resolved'
    }
  ]

  return (
    <section className="recent-tickets">

      <div className="tickets-header">
        <div>
          <h2>Recent Tickets</h2>
          <p>Latest support requests in your organization.</p>
        </div>

        <button className="view-all-button">
          View All
        </button>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Ticket ID</th>
              <th>Subject</th>
              <th>Priority</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            {tickets.map((ticket) => (
              <tr key={ticket.id}>
                <td>{ticket.id}</td>
                <td>{ticket.title}</td>

                <td>
                  <span className={`priority-badge ${ticket.priority.toLowerCase()}`}>
                    {ticket.priority}
                  </span>
                </td>

                <td>
                  <span className={`status-badge ${ticket.status.toLowerCase().replace(' ', '-')}`}>
                    {ticket.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </section>
  )
}

export default RecentTickets
