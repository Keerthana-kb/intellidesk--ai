
import './Sidebar.css'

function Sidebar() {
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

        <a href="#" className="menu-item active">
          <span>▦</span> Dashboard
        </a>

        <a href="#" className="menu-item">
          <span>▤</span> All Tickets
        </a>

        <a href="#" className="menu-item">
          <span>◷</span> My Tickets
        </a>

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
