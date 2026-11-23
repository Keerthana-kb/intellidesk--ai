
import { useState, useEffect } from 'react'

import './App.css'

import Sidebar from './components/Sidebar'
import StatCard from './components/StatCard'
import RecentTickets from './components/RecentTickets'
import SLAOverview from './components/SLAOverview'
import Login from './pages/Login'
import api from './services/api'

function App() {

  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Verify existing login session when application starts.
  useEffect(() => {

    const verifySession = async () => {

      const token = localStorage.getItem('access_token')

      if (!token) {
        setLoading(false)
        return
      }

      try {
        const response = await api.get('/auth/me', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })

        setUser(response.data)

      } catch (error) {
        localStorage.removeItem('access_token')
        setUser(null)

      } finally {
        setLoading(false)
      }
    }

    verifySession()

  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
  }

  if (loading) {
    return <div>Loading IntelliDesk...</div>
  }

  if (!user) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <div className="app-layout">

      <Sidebar />

      <main className="main-content">

        <header className="page-header">

          <div>
            <h1>Dashboard</h1>
            <p>
              Welcome back, {user.full_name}.
              Here's your service desk overview.
            </p>
          </div>

          <button className="primary-button">
            + Create Ticket
          </button>

        </header>

        <section className="dashboard-section">

          <h2>Dashboard Overview</h2>

          <p className="section-description">
            Monitor your IT service desk performance.
          </p>

          <div className="stats-grid">

            <StatCard
              title="Total Tickets"
              value="24"
              description="All tickets"
              color="#172033"
            />

            <StatCard
              title="Open Tickets"
              value="12"
              description="Awaiting action"
              color="#3978e8"
            />

            <StatCard
              title="Resolved Tickets"
              value="9"
              description="Successfully resolved"
              color="#16a34a"
            />

            <StatCard
              title="SLA Breaches"
              value="3"
              description="Require attention"
              color="#dc2626"
            />

          </div>

          <RecentTickets />

          <SLAOverview />

        </section>

      </main>

    </div>
  )
}

export default App
