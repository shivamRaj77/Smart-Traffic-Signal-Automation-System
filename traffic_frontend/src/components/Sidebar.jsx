import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  LayoutDashboard, Activity, Layers, Users, SlidersHorizontal,
  FileText, LogOut, TrafficCone
} from 'lucide-react'

const mainNav = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard', end: true },
  { to: '/simulation', icon: Activity, label: 'Simulation' },
  { to: '/model', icon: Layers, label: 'ML Model' },
]

const adminNav = [
  { to: '/users', icon: Users, label: 'Users' },
  { to: '/overrides', icon: SlidersHorizontal, label: 'Overrides' },
  { to: '/logs', icon: FileText, label: 'Logs' },
]

export default function Sidebar() {
  const { user, logout, isAdmin } = useAuth()
  const roleLabel = user?.role
    ? user.role.charAt(0).toUpperCase() + user.role.slice(1)
    : 'User'
  const usernameLabel = user?.username || 'User'

  const linkClass = ({ isActive }) =>
    `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-[13px] font-medium transition-all duration-150 ${
      isActive
        ? 'bg-[var(--accent-dim)] text-[var(--accent)]'
        : 'text-[var(--txt-secondary)] hover:bg-[var(--border-hover)] hover:text-[var(--txt)]'
    }`

  return (
    <aside className="w-[260px] bg-[var(--bg-surface)] border-r border-[var(--border)] flex flex-col h-screen sticky top-0">
      <div className="px-5 py-6 border-b border-[var(--border)]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-[var(--accent-dim)] flex items-center justify-center">
            <TrafficCone size={18} className="text-[var(--accent)]" />
          </div>
          <div>
            <h1 className="text-[14px] font-bold leading-tight">Traffic Control</h1>
            <p className="text-[10px] font-semibold tracking-[0.08em] uppercase text-[var(--accent)]">Smart City Engine</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 flex flex-col gap-0.5">
        <p className="text-[10px] uppercase tracking-[0.1em] text-[var(--txt-muted)] font-semibold px-3.5 mb-2">Main</p>
        {mainNav.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.end} className={linkClass}>
            <item.icon size={17} />
            {item.label}
          </NavLink>
        ))}

        {isAdmin && (
          <>
            <p className="text-[10px] uppercase tracking-[0.1em] text-[var(--txt-muted)] font-semibold px-3.5 mt-5 mb-2">Admin</p>
            {adminNav.map((item) => (
              <NavLink key={item.to} to={item.to} className={linkClass}>
                <item.icon size={17} />
                {item.label}
              </NavLink>
            ))}
          </>
        )}
      </nav>

      <div className="px-5 py-4 border-t border-[var(--border)]">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[13px] font-semibold">{usernameLabel}</p>
            <p className="text-[11px] text-[var(--txt-muted)]">{roleLabel}</p>
          </div>
          <button
            onClick={logout}
            className="p-2 rounded-lg text-[var(--txt-muted)] hover:text-[var(--danger)] hover:bg-[var(--danger-dim)] transition-all"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  )
}
