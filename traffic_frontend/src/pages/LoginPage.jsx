import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { TrafficCone, ArrowRight } from 'lucide-react'
import api from '../lib/api'

export default function LoginPage() {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await api.post('/auth/login', { username, password })
      login(data.access_token)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Connection failed. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'var(--bg-deep)' }}>
      {/* Ambient glow */}
      <div className="fixed top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full opacity-[0.04] pointer-events-none" style={{ background: 'radial-gradient(circle, var(--accent), transparent 70%)' }} />

      <div className="w-full max-w-[420px] animate-in">
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-[var(--accent-dim)] flex items-center justify-center mx-auto mb-4">
            <TrafficCone size={26} className="text-[var(--accent)]" />
          </div>
          <h1 className="text-[24px] font-bold tracking-tight">Welcome back</h1>
          <p className="text-[14px] text-[var(--txt-secondary)] mt-1">Sign in to the traffic control system</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-8 shadow-2xl shadow-black/40">
          <div className="mb-4">
            <label className="block text-[12px] font-semibold text-[var(--txt-secondary)] uppercase tracking-[0.05em] mb-1.5">Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg text-[14px] text-[var(--txt)] outline-none focus:border-[var(--accent)] transition-colors placeholder:text-[var(--txt-muted)]"
              placeholder="admin"
            />
          </div>
          <div className="mb-6">
            <label className="block text-[12px] font-semibold text-[var(--txt-secondary)] uppercase tracking-[0.05em] mb-1.5">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg text-[14px] text-[var(--txt)] outline-none focus:border-[var(--accent)] transition-colors placeholder:text-[var(--txt-muted)]"
              placeholder="••••••"
            />
          </div>

          {error && (
            <p className="text-[12px] text-[var(--danger)] mb-4 bg-[var(--danger-dim)] px-3 py-2 rounded-lg">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-2.5 bg-[var(--accent)] text-[var(--bg-deep)] font-semibold text-[14px] rounded-lg hover:shadow-lg hover:shadow-[var(--accent-glow)] transition-all active:scale-[0.98] disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign In'}
            {!loading && <ArrowRight size={16} />}
          </button>

          <p className="text-center text-[13px] text-[var(--txt-muted)] mt-5">
            No account?{' '}
            <Link to="/register" className="text-[var(--accent)] font-medium hover:underline">Register</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
