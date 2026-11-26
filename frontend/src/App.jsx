
import { useState, useEffect } from 'react'

import './App.css'

import Sidebar from './components/Sidebar'
import StatCard from './components/StatCard'
import RecentTickets from './components/RecentTickets'
import SLAOverview from './components/SLAOverview'

import Login from './pages/Login'
import CreateTicket from './pages/CreateTicket'
import MyTickets from './pages/MyTickets'
import TicketDetails from './pages/TicketDetails'

import api from './services/api'

function App() {

  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Current page
  const [activePage, setActivePage] = useState('dashboard')

  // Selected ticket ID
  const [selectedTicketId, setSelectedTicketId] = useState(null)

  // Refresh dashboard data after ticket creation
  const [refreshKey, setRefreshKey] = useState(0)

  // Dashboard statistics
  const [dashboardStats, setDashboardStats] = useState(null)
  const [statsLoading, setStatsLoading] = useState(false)
  const [statsError, setStatsError] = useState('')

  // Verify existing login session.
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

  // Fetch dashboard statistics.
  useEffect(() => {

    if (!user) return

    const fetchDashboardStats = async () => {

      setStatsLoading(true)
      setStatsError('')

      try {
        const token = localStorage.getItem('access_token')

        const response = await api.get('/dashboard/stats', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })

        setDashboardStats(response.data)

      } catch (error) {
        console.error('Dashboard API error:', error)
        setStatsError('Unable to load dashboard statistics.')

      } finally {
        setStatsLoading(false)
      }
    }

    fetchDashboardStats()

  }, [user, refreshKey])

  // Login handler
  const handleLogin = (userData) => {
    setUser(userData)
  }

  // Ticket creation handler
  const handleTicketCreated = () => {
    setRefreshKey((previousKey) => previousKey + 1)
  }

  // Ticket selection handler
  const handleTicketSelect = (ticketId) => {
    setSelectedTicketId(ticketId)
    setActivePage('ticket-details')
  }

  // Loading screen
  if (loading) {
    return <div>Loading IntelliDesk...</div>
  }

  // Login screen
  if (!user) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <div className="app-layout">

      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
      />

      <main className="main-content">

        {/* DASHBOARD */}

        {activePage === 'dashboard' && (

          <>
            <header className="page-header">

              <div>
                <h1>Dashboard</h1>
                <p>
                  Welcome back, {user.full_name}.
                  Here's your service desk overview.
                </p>
              </div>

              <button
                className="primary-button"
                onClick={() => setActivePage('create-ticket')}
              >
                + Create Ticket
              </button>

            </header>

            <section className="dashboard-section">

              <h2>Dashboard Overview</h2>

              <p className="section-description">
                Monitor your IT service desk performance.
              </p>

              {statsError && (
                <p className="login-error">
                  {statsError}
                </p>
              )}

              <div className="stats-grid">

                <StatCard
                  title="Total Tickets"
                  value={
                    statsLoading
                      ? '...'
                      : dashboardStats?.total_tickets ?? 0
                  }
                  description="All tickets"
                  color="#172033"
                />

                <StatCard
                  title="Open Tickets"
                  value={
                    statsLoading
                      ? '...'
                      : dashboardStats?.open_tickets ?? 0
                  }
                  description="Awaiting action"
                  color="#3978e8"
                />

                <StatCard
                  title="Resolved Tickets"
                  value={
                    statsLoading
                      ? '...'
                      : dashboardStats?.resolved_tickets ?? 0
                  }
                  description="Successfully resolved"
                  color="#16a34a"
                />

                <StatCard
                  title="SLA Breaches"
                  value={
                    statsLoading
                      ? '...'
                      : dashboardStats?.sla_breaches ?? 0
                  }
                  description="Require attention"
                  color="#dc2626"
                />

              </div>

              <RecentTickets />

              <SLAOverview />

            </section>
          </>

        )}

        {/* CREATE TICKET */}

        {activePage === 'create-ticket' && (

          <CreateTicket
            onTicketCreated={handleTicketCreated}
            onCancel={() => setActivePage('dashboard')}
          />

        )}

        {/* MY TICKETS */}

        {activePage === 'my-tickets' && (

          <MyTickets
            onTicketSelect={handleTicketSelect}
          />

        )}

        {/* TICKET DETAILS */}

        {activePage === 'ticket-details' && (

          <TicketDetails
            ticketId={selectedTicketId}
            onBack={() => setActivePage('my-tickets')}
          />

        )}

      </main>

    </div>
  )
}

export default App
