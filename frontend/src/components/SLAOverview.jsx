
import { useState, useEffect } from 'react'
import api from '../services/api'
import './SLAOverview.css'

function SLAOverview() {

  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Fetch actual tickets from backend
  useEffect(() => {

    const fetchTickets = async () => {

      try {
        const token = localStorage.getItem('access_token')

        const response = await api.get('/tickets/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })

        setTickets(response.data)

      } catch (error) {
        console.error('Error fetching SLA data:', error)
        setError('Unable to load SLA information.')

      } finally {
        setLoading(false)
      }
    }

    fetchTickets()

  }, [])

  // Check whether an SLA was completed within its deadline
  const isWithinDeadline = (completedAt, dueAt) => {

    if (!completedAt || !dueAt) {
      return false
    }

    return new Date(completedAt) <= new Date(dueAt)
  }

  // Tickets with response SLA deadlines
  const responseEligible = tickets.filter(
    ticket => ticket.response_due_at
  )

  // Tickets with resolution SLA deadlines
  const resolutionEligible = tickets.filter(
    ticket => ticket.resolution_due_at
  )

  // Successfully completed within response deadline
  const responseCompleted = responseEligible.filter(
    ticket => isWithinDeadline(
      ticket.first_response_at,
      ticket.response_due_at
    )
  ).length

  // Successfully resolved within resolution deadline
  const resolutionCompleted = resolutionEligible.filter(
    ticket => isWithinDeadline(
      ticket.resolved_at,
      ticket.resolution_due_at
    )
  ).length

  // Calculate SLA completion percentages
  const responseRate = responseEligible.length
    ? Math.round(
        (responseCompleted / responseEligible.length) * 100
      )
    : 0

  const resolutionRate = resolutionEligible.length
    ? Math.round(
        (resolutionCompleted / resolutionEligible.length) * 100
      )
    : 0

  // Count response SLA breaches
  const responseBreaches = tickets.filter(ticket =>
    ticket.response_breached ||
    (
      ticket.first_response_at &&
      ticket.response_due_at &&
      !isWithinDeadline(
        ticket.first_response_at,
        ticket.response_due_at
      )
    )
  ).length

  // Count resolution SLA breaches
  const resolutionBreaches = tickets.filter(ticket =>
    ticket.resolution_breached ||
    (
      ticket.resolved_at &&
      ticket.resolution_due_at &&
      !isWithinDeadline(
        ticket.resolved_at,
        ticket.resolution_due_at
      )
    )
  ).length

  // Count each breached ticket only once
  const totalBreaches = tickets.filter(ticket =>
    ticket.response_breached ||
    ticket.resolution_breached ||
    (
      ticket.first_response_at &&
      ticket.response_due_at &&
      !isWithinDeadline(
        ticket.first_response_at,
        ticket.response_due_at
      )
    ) ||
    (
      ticket.resolved_at &&
      ticket.resolution_due_at &&
      !isWithinDeadline(
        ticket.resolved_at,
        ticket.resolution_due_at
      )
    )
  ).length

  if (loading) {
    return (
      <section className="sla-overview">
        <h2>SLA Overview</h2>
        <p>Loading SLA information...</p>
      </section>
    )
  }

  if (error) {
    return (
      <section className="sla-overview">
        <h2>SLA Overview</h2>
        <p>{error}</p>
      </section>
    )
  }

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
          <p>
            {responseCompleted} of {responseEligible.length}
            {' '}tickets responded to within deadline
          </p>
        </div>

        <div className="sla-card">
          <span>Resolution Completion</span>
          <h3>{resolutionRate}%</h3>
          <p>
            {resolutionCompleted} of {resolutionEligible.length}
            {' '}tickets resolved within deadline
          </p>
        </div>

        <div className="sla-card">
          <span>Response Breaches</span>
          <h3 className="breach-number">
            {responseBreaches}
          </h3>
          <p>Response deadlines missed</p>
        </div>

        <div className="sla-card">
          <span>Resolution Breaches</span>
          <h3 className="breach-number">
            {resolutionBreaches}
          </h3>
          <p>Resolution deadlines missed</p>
        </div>

      </div>

      <div className="sla-total">
        Total tickets with at least one SLA breach:{' '}
        <strong>{totalBreaches}</strong>
      </div>

    </section>
  )
}

export default SLAOverview
