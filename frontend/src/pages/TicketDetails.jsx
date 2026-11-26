
import { useState, useEffect } from 'react'
import api from '../services/api'
import './TicketDetails.css'

function TicketDetails({ ticketId, onBack }) {

  const [ticket, setTicket] = useState(null)
  const [comments, setComments] = useState([])
  const [events, setEvents] = useState([])

  const [loading, setLoading] = useState(true)
  const [commentsLoading, setCommentsLoading] = useState(true)
  const [eventsLoading, setEventsLoading] = useState(true)

  const [error, setError] = useState('')
  const [commentError, setCommentError] = useState('')

  const [newComment, setNewComment] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // Status management states
  const [selectedStatus, setSelectedStatus] = useState('')
  const [statusUpdating, setStatusUpdating] = useState(false)
  const [statusError, setStatusError] = useState('')
  const [statusMessage, setStatusMessage] = useState('')

  // Priority management states
  const [selectedPriority, setSelectedPriority] = useState('')
  const [priorityUpdating, setPriorityUpdating] = useState(false)
  const [priorityError, setPriorityError] = useState('')
  const [priorityMessage, setPriorityMessage] = useState('')

  // Fetch ticket details, comments and events.
  useEffect(() => {

    const token = localStorage.getItem('access_token')

    const headers = {
      Authorization: `Bearer ${token}`
    }

    const fetchTicketDetails = async () => {

      try {
        setLoading(true)
        setError('')

        const response = await api.get(
          `/tickets/${ticketId}`,
          { headers }
        )

        setTicket(response.data)
        setSelectedStatus(response.data.status)
        setSelectedPriority(response.data.priority)

      } catch (error) {
        console.error('Ticket Details API error:', error)

        setError(
          error.response?.data?.detail ||
          'Unable to load ticket details.'
        )

      } finally {
        setLoading(false)
      }
    }

    const fetchComments = async () => {

      try {
        setCommentsLoading(true)
        setCommentError('')

        const response = await api.get(
          `/tickets/${ticketId}/comments`,
          { headers }
        )

        setComments(response.data)

      } catch (error) {
        console.error('Comments API error:', error)
        setCommentError('Unable to load comments.')

      } finally {
        setCommentsLoading(false)
      }
    }

    const fetchEvents = async () => {

      try {
        setEventsLoading(true)

        const response = await api.get(
          `/tickets/${ticketId}/events`,
          { headers }
        )

        setEvents(response.data)

      } catch (error) {
        console.error('Ticket Events API error:', error)

      } finally {
        setEventsLoading(false)
      }
    }

    if (ticketId) {
      fetchTicketDetails()
      fetchComments()
      fetchEvents()
    }

  }, [ticketId])

  // Update ticket status.
  const handleStatusUpdate = async () => {

    if (!selectedStatus || selectedStatus === ticket.status) {
      return
    }

    try {
      setStatusUpdating(true)
      setStatusError('')
      setStatusMessage('')

      const token = localStorage.getItem('access_token')

      const response = await api.patch(
        `/tickets/${ticketId}/status`,
        {
          status: selectedStatus
        },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )

      setTicket(response.data)
      setSelectedStatus(response.data.status)
      setStatusMessage('Ticket status updated successfully!')

      // Refresh activity timeline.
      const eventsResponse = await api.get(
        `/tickets/${ticketId}/events`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )

      setEvents(eventsResponse.data)

    } catch (error) {
      console.error('Status update API error:', error)

      setStatusError(
        error.response?.data?.detail ||
        'Unable to update ticket status.'
      )

      setSelectedStatus(ticket.status)

    } finally {
      setStatusUpdating(false)
    }
  }

  // Update ticket priority.
  const handlePriorityUpdate = async () => {

    if (!selectedPriority || selectedPriority === ticket.priority) {
      return
    }

    try {
      setPriorityUpdating(true)
      setPriorityError('')
      setPriorityMessage('')

      const token = localStorage.getItem('access_token')

      const response = await api.patch(
        `/tickets/${ticketId}/priority`,
        {
          priority: selectedPriority
        },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )

      // Update ticket information and SLA deadlines.
      setTicket(response.data)
      setSelectedPriority(response.data.priority)

      setPriorityMessage('Ticket priority updated successfully!')

      // Refresh activity timeline.
      const eventsResponse = await api.get(
        `/tickets/${ticketId}/events`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )

      setEvents(eventsResponse.data)

    } catch (error) {
      console.error('Priority update API error:', error)

      setPriorityError(
        error.response?.data?.detail ||
        'Unable to update ticket priority.'
      )

      setSelectedPriority(ticket.priority)

    } finally {
      setPriorityUpdating(false)
    }
  }

  // Submit a new comment.
  const handleAddComment = async (event) => {

    event.preventDefault()

    if (!newComment.trim()) {
      setCommentError('Please enter a comment.')
      return
    }

    try {
      setSubmitting(true)
      setCommentError('')

      const token = localStorage.getItem('access_token')

      const response = await api.post(
        `/tickets/${ticketId}/comments`,
        {
          comment: newComment.trim()
        },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )

      setComments((previousComments) => [
        ...previousComments,
        response.data
      ])

      setNewComment('')

      // Refresh activity timeline.
      const eventsResponse = await api.get(
        `/tickets/${ticketId}/events`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )

      setEvents(eventsResponse.data)

    } catch (error) {
      console.error('Add comment API error:', error)

      setCommentError(
        error.response?.data?.detail ||
        'Unable to add comment. Please try again.'
      )

    } finally {
      setSubmitting(false)
    }
  }

  // Format date and time.
  const formatDate = (date) => {

    if (!date) return 'Not available'

    return new Date(date).toLocaleString()
  }

  // Convert event types into readable descriptions.
  const getEventDescription = (event) => {

    switch (event.event_type) {

      case 'ticket_created':
        return 'Ticket was created.'

      case 'status_changed':
        return `Status changed from ${event.old_value} to ${event.new_value}.`

      case 'priority_changed':
        return `Priority changed from ${event.old_value} to ${event.new_value}.`

      case 'ticket_assigned':
        return `Ticket assigned to ${event.new_value}.`

      case 'comment_added':
        return 'A comment was added.'

      case 'resolution_recorded':
        return 'Ticket resolution was recorded.'

      default:
        return event.event_type.replaceAll('_', ' ')
    }
  }

  // Loading screen.
  if (loading) {
    return (
      <div className="ticket-details-page">
        <p>Loading ticket details...</p>
      </div>
    )
  }

  // Error screen.
  if (error) {
    return (
      <div className="ticket-details-page">

        <button className="back-button" onClick={onBack}>
          Back to My Tickets
        </button>

        <p className="details-error">{error}</p>

      </div>
    )
  }

  if (!ticket) return null

  return (
    <section className="ticket-details-page">

      <div className="details-header">

        <div>
          <h2>Ticket Details</h2>
          <p>View complete information about your support request.</p>
        </div>

        <button className="back-button" onClick={onBack}>
          Back to My Tickets
        </button>

      </div>

      {/* TICKET INFORMATION */}

      <div className="ticket-details-card">

        <div className="ticket-title-section">

          <div>
            <span className="details-label">TICKET ID</span>
            <p className="ticket-id">{ticket.id}</p>
          </div>

          <div className="ticket-badges">

            <span className={`priority-badge ${ticket.priority}`}>
              {ticket.priority}
            </span>

            <span className={`status-badge ${ticket.status}`}>
              {ticket.status.replace('_', ' ')}
            </span>

          </div>

        </div>

        <div className="details-divider"></div>

        <div className="ticket-information">

          <h3>{ticket.title}</h3>

          <div className="detail-item">
            <span className="details-label">DESCRIPTION</span>
            <p>{ticket.description}</p>
          </div>

          <div className="detail-grid">

            <div className="detail-item">
              <span className="details-label">CATEGORY</span>
              <p>{ticket.category || 'Not specified'}</p>
            </div>

            <div className="detail-item">
              <span className="details-label">CREATED DATE</span>
              <p>{formatDate(ticket.created_at)}</p>
            </div>

          </div>

        </div>

      </div>

      {/* STATUS MANAGEMENT */}

      <div className="ticket-details-card status-management-section">

        <h3>Manage Ticket Status</h3>

        <label htmlFor="ticket-status">
          Select New Status
        </label>

        <div className="status-update-controls">

          <select
            id="ticket-status"
            value={selectedStatus}
            onChange={(event) => {
              setSelectedStatus(event.target.value)
              setStatusError('')
              setStatusMessage('')
            }}
          >
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>

          <button
            className="update-status-button"
            onClick={handleStatusUpdate}
            disabled={
              statusUpdating ||
              selectedStatus === ticket.status
            }
          >
            {statusUpdating ? 'Updating...' : 'Update Status'}
          </button>

        </div>

        {statusError && (
          <p className="status-error">{statusError}</p>
        )}

        {statusMessage && (
          <p className="status-success">{statusMessage}</p>
        )}

      </div>

      {/* PRIORITY MANAGEMENT */}

      <div className="ticket-details-card priority-management-section">

        <h3>Manage Ticket Priority</h3>

        <label htmlFor="ticket-priority">
          Select New Priority
        </label>

        <div className="priority-update-controls">

          <select
            id="ticket-priority"
            value={selectedPriority}
            onChange={(event) => {
              setSelectedPriority(event.target.value)
              setPriorityError('')
              setPriorityMessage('')
            }}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>

          <button
            className="update-priority-button"
            onClick={handlePriorityUpdate}
            disabled={
              priorityUpdating ||
              selectedPriority === ticket.priority
            }
          >
            {priorityUpdating ? 'Updating...' : 'Update Priority'}
          </button>

        </div>

        {priorityError && (
          <p className="priority-error">{priorityError}</p>
        )}

        {priorityMessage && (
          <p className="priority-success">{priorityMessage}</p>
        )}

      </div>

      {/* SLA INFORMATION */}

      <div className="ticket-details-card">

        <h3>SLA Information</h3>

        <div className="sla-details-grid">

          <div className="sla-detail-item">
            <span className="details-label">FIRST RESPONSE</span>
            <p>{formatDate(ticket.first_response_at)}</p>
          </div>

          <div className="sla-detail-item">
            <span className="details-label">RESPONSE DEADLINE</span>
            <p>{formatDate(ticket.response_due_at)}</p>

            <span className={`sla-status ${ticket.response_breached ? 'breached' : 'safe'}`}>
              {ticket.response_breached ? 'Breached' : 'Not breached'}
            </span>
          </div>

          <div className="sla-detail-item">
            <span className="details-label">RESOLVED DATE</span>
            <p>{formatDate(ticket.resolved_at)}</p>
          </div>

          <div className="sla-detail-item">
            <span className="details-label">RESOLUTION DEADLINE</span>
            <p>{formatDate(ticket.resolution_due_at)}</p>

            <span className={`sla-status ${ticket.resolution_breached ? 'breached' : 'safe'}`}>
              {ticket.resolution_breached ? 'Breached' : 'Not breached'}
            </span>
          </div>

        </div>

      </div>

      {/* COMMENTS SECTION */}

      <div className="ticket-details-card comments-section">

        <div className="comments-header">
          <h3>Comments</h3>
          <span>{comments.length} Comments</span>
        </div>

        {commentsLoading ? (

          <p>Loading comments...</p>

        ) : comments.length === 0 ? (

          <div className="no-comments">
            <p>No comments yet.</p>
            <span>Be the first to add a comment.</span>
          </div>

        ) : (

          <div className="comments-list">

            {comments.map((comment) => (

              <div className="comment-item" key={comment.id}>

                <div className="comment-header">

                  <strong>{comment.user_name}</strong>

                  <span>{formatDate(comment.created_at)}</span>

                </div>

                <p>{comment.comment}</p>

              </div>

            ))}

          </div>

        )}

        <form
          className="add-comment-form"
          onSubmit={handleAddComment}
        >

          <label htmlFor="new-comment">
            Add a Comment
          </label>

          <textarea
            id="new-comment"
            value={newComment}
            onChange={(event) => setNewComment(event.target.value)}
            placeholder="Write your comment here..."
            rows={4}
            maxLength={5000}
            required
          />

          <div className="comment-form-footer">

            <span>{newComment.length}/5000 characters</span>

            <button
              type="submit"
              className="submit-comment-button"
              disabled={submitting || !newComment.trim()}
            >
              {submitting ? 'Posting...' : 'Post Comment'}
            </button>

          </div>

          {commentError && (
            <p className="comment-error">{commentError}</p>
          )}

        </form>

      </div>

      {/* ACTIVITY TIMELINE */}

      <div className="ticket-details-card activity-section">

        <h3>Activity Timeline</h3>

        {eventsLoading ? (

          <p>Loading activity...</p>

        ) : events.length === 0 ? (

          <p className="no-activity">
            No activity recorded yet.
          </p>

        ) : (

          <div className="activity-list">

            {events.map((event) => (

              <div className="activity-item" key={event.id}>

                <div className="activity-marker"></div>

                <div className="activity-content">

                  <strong>
                    {event.user_name || 'System'}
                  </strong>

                  <p>{getEventDescription(event)}</p>

                  <span>{formatDate(event.created_at)}</span>

                </div>

              </div>

            ))}

          </div>

        )}

      </div>

    </section>
  )
}

export default TicketDetails
