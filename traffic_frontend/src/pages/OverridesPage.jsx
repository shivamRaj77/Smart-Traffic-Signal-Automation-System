import { useState, useEffect } from 'react'
import { Plus, Loader, RefreshCw } from 'lucide-react'
import { PageHeader, useToast } from '../components/UI'
import api from '../lib/api'

const JUNCTIONS = ['J1','J2','J3','J4','J5','J6','J7','J8','J9']
const DIRECTIONS = ['north','south','east','west']

export default function OverridesPage() {
  const [overrides, setOverrides] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [junction, setJunction] = useState('J1')
  const [direction, setDirection] = useState('north')
  const [greenTime, setGreenTime] = useState(30)
  const toast = useToast()

  async function loadOverrides() {
    setLoading(true)
    try {
      const { data } = await api.get('/admin/overrides')
      setOverrides(data)
    } catch (err) {
      toast(err.response?.data?.detail || 'Failed to load overrides', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadOverrides() }, [])

  async function createOverride(e) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await api.post('/admin/override', { junction_id: junction, direction, green_time: greenTime })
      toast('Override created')
      loadOverrides()
    } catch (err) {
      toast(err.response?.data?.detail || 'Failed to create override', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  const selectClass = "w-full px-3.5 py-2.5 bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg text-[14px] text-[var(--txt)] outline-none focus:border-[var(--accent)] transition-colors appearance-none"
  const labelClass = "block text-[12px] font-semibold text-[var(--txt-secondary)] uppercase tracking-[0.05em] mb-1.5"

  return (
    <div className="animate-in">
      <PageHeader title="Signal Overrides">
        <button
          onClick={loadOverrides}
          className="flex items-center gap-2 px-4 py-2 text-[13px] font-medium text-[var(--txt-secondary)] border border-[var(--border-hover)] rounded-lg hover:border-[var(--accent)] hover:text-[var(--accent)] transition-all"
        >
          <RefreshCw size={14} /> Refresh
        </button>
      </PageHeader>

      {/* Override Form */}
      <form onSubmit={createOverride} className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-5 mb-6">
        <h4 className="text-[13px] font-semibold text-[var(--txt-secondary)] mb-4">Create New Override</h4>
        <div className="grid grid-cols-4 gap-4 items-end">
          <div>
            <label className={labelClass}>Junction</label>
            <select value={junction} onChange={(e) => setJunction(e.target.value)} className={selectClass}>
              {JUNCTIONS.map((j) => <option key={j} value={j}>{j}</option>)}
            </select>
          </div>
          <div>
            <label className={labelClass}>Direction</label>
            <select value={direction} onChange={(e) => setDirection(e.target.value)} className={selectClass}>
              {DIRECTIONS.map((d) => <option key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</option>)}
            </select>
          </div>
          <div>
            <label className={labelClass}>Green Time (s)</label>
            <input
              type="number"
              min={5}
              max={120}
              value={greenTime}
              onChange={(e) => setGreenTime(parseInt(e.target.value) || 5)}
              className={selectClass}
            />
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="flex items-center justify-center gap-2 py-2.5 bg-[var(--accent)] text-[var(--bg-deep)] font-semibold text-[13px] rounded-lg hover:shadow-lg hover:shadow-[var(--accent-glow)] transition-all active:scale-[0.98] disabled:opacity-50"
          >
            <Plus size={14} />
            {submitting ? 'Creating...' : 'Set Override'}
          </button>
        </div>
      </form>

      {/* Overrides Table */}
      {loading ? (
        <div className="flex items-center justify-center py-16 text-[var(--txt-muted)]">
          <Loader size={20} className="animate-spin mr-3" /> Loading overrides...
        </div>
      ) : overrides.length === 0 ? (
        <div className="text-center py-16 text-[var(--txt-muted)]">
          <p className="text-[14px]">No overrides set. Create one above to manually control signal timing.</p>
        </div>
      ) : (
        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl overflow-hidden">
          <div className="px-5 py-3.5 border-b border-[var(--border)]">
            <h3 className="text-[14px] font-semibold">{overrides.length} Active Override{overrides.length > 1 ? 's' : ''}</h3>
          </div>
          <table className="w-full text-[13px]">
            <thead>
              <tr>
                {['ID', 'Junction', 'Direction', 'Green Time', 'Set By', 'Created'].map((h) => (
                  <th key={h} className="text-left px-5 py-2.5 text-[11px] font-semibold uppercase tracking-[0.06em] text-[var(--txt-muted)] border-b border-[var(--border)]">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {overrides.map((o, i) => (
                <tr key={o.id} className="hover:bg-[var(--bg-card-hover)] transition-colors animate-in" style={{ animationDelay: `${i * 30}ms` }}>
                  <td className="px-5 py-3"><code className="text-[11px] text-[var(--txt-muted)]" style={{ fontFamily: 'var(--font-mono)' }}>{o.id}</code></td>
                  <td className="px-5 py-3 font-semibold text-[var(--txt)]">{o.junction_id}</td>
                  <td className="px-5 py-3 capitalize text-[var(--txt-secondary)]">{o.direction}</td>
                  <td className="px-5 py-3"><span className="font-semibold text-[var(--success)]" style={{ fontFamily: 'var(--font-mono)' }}>{o.green_time}s</span></td>
                  <td className="px-5 py-3 text-[var(--txt-secondary)]">{o.set_by}</td>
                  <td className="px-5 py-3 text-[var(--txt-secondary)]">{new Date(o.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
