
import './Sidebar.css'

function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">

      <div className="sidebar-brand">
        <div className="brand-icon">I</div>
        <div>
          <h2>IntelliDesk</h2>
          <span>AI SERVICE DESK</span>
        </div>
      </div>

      <div className="sidebar-menu">
        <p className="menu-heading">WORKSPACE</p>

        <button
          className={`menu-item ${activePage === 'dashboard' ? 'active' : ''}`}
          onClick={() => onNavigate('dashboard')}
        >
          <span>▦</span> Dashboard
        </button>

        <a href="#" className="menu-item">
          <span>▤</span> All Tickets
        </a>

        <button
          className={`menu-item ${activePage === 'my-tickets' ? 'active' : ''}`}
          onClick={() => onNavigate('my-tickets')}
        >
          <span>◷</span> My Tickets
        </button>

        <a href="#" className="menu-item">
          <span>♧</span> Teams
        </a>

        <p className="menu-heading">INTELLIGENCE</p>

        <a href="#" className="menu-item">
          <span>◷</span> SLA Monitoring
        </a>

        <a href="#" className="menu-item">
          <span>✧</span> AI Insights
        </a>

        <p className="menu-heading">SYSTEM</p>

        <a href="#" className="menu-item">
          <span>⚙</span> Settings
        </a>
      </div>

      <div className="sidebar-profile">
        <div className="profile-avatar">K</div>
        <div>
          <h4>Administrator</h4>
          <span>Admin Account</span>
        </div>
      </div>

    </aside>
  )
}

export default Sidebar
