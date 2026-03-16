import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import { useAuth } from '../context/AuthContext'
import { Play } from 'lucide-react'

const pageTitles = {
  '/': 'Dashboard',
  '/simulation': 'Simulation Results',
  '/model': 'ML Model',
  '/users': 'User Management',
  '/overrides': 'Signal Overrides',
  '/logs': 'Simulation Logs',
}

export default function Layout() {
  const location = useLocation()
  const { user } = useAuth()
  const title = pageTitles[location.pathname] || 'Dashboard'

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <header className="sticky top-0 z-50 px-8 py-4 flex items-center justify-between border-b border-[var(--border)] backdrop-blur-xl bg-[var(--bg-deep)]/80">
          <h2 className="text-[16px] font-semibold">{title}</h2>
          <div className="flex items-center gap-3">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
              user?.role === 'admin'
                ? 'bg-[var(--accent-dim)] text-[var(--accent)]'
                : 'bg-[var(--success-dim)] text-[var(--success)]'
            }`}>
              {user?.role?.toUpperCase()}
            </span>
          </div>
        </header>
        <main className="flex-1 p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
