
import { useState } from 'react'
import api from '../services/api'
import './CreateTicket.css'

function CreateTicket({ onTicketCreated, onCancel }) {

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    priority: 'medium'
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleChange = (event) => {
    const { name, value } = event.target

    setFormData((previousData) => ({
      ...previousData,
      [name]: value
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()

    setError('')
    setSuccess('')

    if (formData.title.trim().length < 5) {
      setError('Title must contain at least 5 characters.')
      return
    }

    if (formData.title.trim().length > 200) {
      setError('Title cannot exceed 200 characters.')
      return
    }

    if (formData.description.trim().length < 10) {
      setError('Description must contain at least 10 characters.')
      return
    }

    try {
      setLoading(true)

      const token = localStorage.getItem('access_token')

      const response = await api.post('/tickets/', {
        ...formData,
        title: formData.title.trim(),
        description: formData.description.trim(),
        category: formData.category.trim() || null
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })

      setSuccess('Ticket created successfully!')

      if (onTicketCreated) {
        onTicketCreated(response.data)
      }

      setFormData({
        title: '',
        description: '',
        category: '',
        priority: 'medium'
      })

    } catch (error) {
      setError(
        error.response?.data?.detail ||
        'Unable to create ticket. Please try again.'
      )

    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="create-ticket-page">

      <div className="create-ticket-header">
        <div>
          <h2>Create New Ticket</h2>
          <p>Submit a new IT support request.</p>
        </div>

        <button
          type="button"
          className="cancel-button"
          onClick={onCancel}
        >
          Cancel
        </button>
      </div>

      <form
        className="create-ticket-form"
        onSubmit={handleSubmit}
      >

        <label htmlFor="title">Ticket Title</label>

        <input
          id="title"
          name="title"
          type="text"
          placeholder="Enter ticket title"
          value={formData.title}
          onChange={handleChange}
          minLength={5}
          maxLength={200}
          required
        />

        <label htmlFor="description">Description</label>

        <textarea
          id="description"
          name="description"
          placeholder="Describe your IT issue..."
          value={formData.description}
          onChange={handleChange}
          minLength={10}
          required
          rows={5}
        />

        <label htmlFor="category">Category</label>

        <select
          id="category"
          name="category"
          value={formData.category}
          onChange={handleChange}
        >
          <option value="">Select category</option>
          <option value="Network">Network</option>
          <option value="Hardware">Hardware</option>
          <option value="Software">Software</option>
          <option value="Access">Access</option>
          <option value="Other">Other</option>
        </select>

        <label htmlFor="priority">Priority</label>

        <select
          id="priority"
          name="priority"
          value={formData.priority}
          onChange={handleChange}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>

        {error && (
          <p className="ticket-error">{error}</p>
        )}

        {success && (
          <p className="ticket-success">{success}</p>
        )}

        <button
          type="submit"
          className="submit-ticket-button"
          disabled={loading}
        >
          {loading ? 'Creating Ticket...' : 'Create Ticket'}
        </button>

      </form>

    </section>
  )
}

export default CreateTicket
