
import { useState } from 'react'
import api from '../services/api'
import './Login.css'

function Login({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (event) => {
    event.preventDefault()

    setError('')
    setLoading(true)

    try {
      const response = await api.post('/auth/login', {
        email,
        password
      })

      const token = response.data.access_token

      localStorage.setItem('access_token', token)

      const profileResponse = await api.get('/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })

      onLogin(profileResponse.data)

    } catch (error) {
      setError(
        error.response?.data?.detail ||
        'Unable to login. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">

      <div className="login-card">

        <div className="login-brand">
          <div className="login-logo">I</div>
          <h1>IntelliDesk AI</h1>
          <p>Intelligent IT Service Management</p>
        </div>

        <form onSubmit={handleLogin}>

          <h2>Welcome Back</h2>
          <p className="login-description">
            Sign in to access your service desk.
          </p>

          <label>Email Address</label>
          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />

          {error && (
            <div className="login-error">
              {error}
            </div>
          )}

          <button type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>

        </form>

      </div>

    </div>
  )
}

export default Login
