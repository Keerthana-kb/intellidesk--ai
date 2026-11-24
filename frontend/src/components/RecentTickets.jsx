
import { useState, useEffect } from 'react'
import api from '../services/api'
import './RecentTickets.css'

function RecentTickets() {

  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Fetch tickets from FastAPI
  useEffect(() => {

    const fetchRecentTickets = async () => {

      try {
        const token = localStorage.getItem('access_token')

        const response = await api.get('/tickets/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })

        // Display the five latest tickets
        setTickets(response.data.slice(0, 5))

      } catch (error) {
        console.error('Error fetching tickets:', error)
        setError('Unable to load recent tickets.')

      } finally {
        setLoading(false)
      }
    }

    fetchRecentTickets()

  }, [])

  // Convert status into readable format
  const formatStatus = (status) => {
    return status
      .replace('_', ' ')
      .replace(/\b\w/g, char => char.toUpperCase())
  }

  // Convert priority into readable format
  const formatPriority = (priority) => {
    return priority.charAt(0).toUpperCase() +
      priority.slice(1)
  }

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

            {loading && (
              <tr>
                <td colSpan="4">Loading tickets...</td>
              </tr>
            )}

            {!loading && error && (
              <tr>
                <td colSpan="4">{error}</td>
              </tr>
            )}

            {!loading && !error && tickets.length === 0 && (
              <tr>
                <td colSpan="4">No tickets found.</td>
              </tr>
            )}

            {!loading && !error && tickets.map((ticket) => (

              <tr key={ticket.id}>

                <td title={ticket.id}>
                  {ticket.id.slice(0, 8)}
                </td>

                <td>{ticket.title}</td>

                <td>
                  <span
                    className={`priority-badge ${ticket.priority.toLowerCase()}`}
                  >
                    {formatPriority(ticket.priority)}
                  </span>
                </td>

                <td>
                  <span
                    className={`status-badge ${ticket.status.toLowerCase().replace(' ', '-')}`}
                  >
                    {formatStatus(ticket.status)}
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
