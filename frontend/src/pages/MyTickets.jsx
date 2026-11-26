
import { useState, useEffect } from 'react'
import api from '../services/api'
import './MyTickets.css'

function MyTickets({ onTicketSelect }) {

  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {

    const fetchMyTickets = async () => {

      try {
        const token = localStorage.getItem('access_token')

        const response = await api.get('/tickets/my-tickets', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })

        setTickets(response.data)

      } catch (error) {
        console.error('My Tickets API error:', error)
        setError(
          error.response?.data?.detail ||
          'Unable to load your tickets.'
        )

      } finally {
        setLoading(false)
      }
    }

    fetchMyTickets()

  }, [])

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString()
  }

  return (
    <section className="my-tickets-page">

      <div className="my-tickets-header">
        <div>
          <h2>My Tickets</h2>
          <p>View and track the IT support requests you submitted.</p>
        </div>

        <div className="ticket-count">
          Total: {tickets.length}
        </div>
      </div>

      {loading && <p>Loading your tickets...</p>}

      {error && <p className="my-tickets-error">{error}</p>}

      {!loading && !error && tickets.length === 0 && (
        <div className="empty-tickets">
          <h3>No tickets found</h3>
          <p>You haven't submitted any support requests yet.</p>
        </div>
      )}

      {!loading && !error && tickets.length > 0 && (

        <div className="my-tickets-table-container">

          <table className="my-tickets-table">

            <thead>
              <tr>
                <th>Ticket ID</th>
                <th>Title</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Created Date</th>
              </tr>
            </thead>

            <tbody>
              {tickets.map((ticket) => (

                <tr
                  key={ticket.id}
                  className="clickable-ticket-row"
                  onClick={() => onTicketSelect(ticket.id)}
                  title="Click to view ticket details"
                  tabIndex={0}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault()
                      onTicketSelect(ticket.id)
                    }
                  }}
                >

                  <td>{ticket.id.slice(0, 8)}</td>

                  <td>{ticket.title}</td>

                  <td>
                    <span className={`priority-badge ${ticket.priority}`}>
                      {ticket.priority}
                    </span>
                  </td>

                  <td>
                    <span className={`status-badge ${ticket.status}`}>
                      {ticket.status.replace('_', ' ')}
                    </span>
                  </td>

                  <td>{formatDate(ticket.created_at)}</td>

                </tr>

              ))}
            </tbody>

          </table>

        </div>

      )}

    </section>
  )
}

export default MyTickets
