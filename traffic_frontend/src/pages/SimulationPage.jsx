import { useState } from 'react'
import { Play, Clock, ChevronDown, ChevronUp } from 'lucide-react'
import { CongestionBadge, congestionColor, EmptyState, PageHeader } from '../components/UI'
import { useToast } from '../components/UI'
import api from '../lib/api'

function JunctionTable({ junction, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen)
  const j = junction
  const dirs = ['north', 'south', 'east', 'west']

  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl overflow-hidden transition-all">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-[var(--bg-card-hover)] transition-colors"
      >
        <div className="flex items-center gap-4">
          <span className="text-[15px] font-bold" style={{ fontFamily: 'var(--font-mono)' }}>{j.junction_id}</span>
          <CongestionBadge value={j.total_congestion} />
          <span className="text-[13px] text-[var(--txt-secondary)]">
            Total: <span className="font-semibold" style={{ color: congestionColor(j.total_congestion), fontFamily: 'var(--font-mono)' }}>
              {(j.total_congestion * 100).toFixed(1)}%
            </span>
          </span>
        </div>
        {open ? <ChevronUp size={16} className="text-[var(--txt-muted)]" /> : <ChevronDown size={16} className="text-[var(--txt-muted)]" />}
      </button>

      {open && (
        <div className="border-t border-[var(--border)] animate-in">
          <table className="w-full text-[13px]">
            <thead>
              <tr>
                <th className="text-left px-5 py-2.5 text-[11px] font-semibold uppercase tracking-[0.06em] text-[var(--txt-muted)] border-b border-[var(--border)]">Direction</th>
                <th className="text-left px-5 py-2.5 text-[11px] font-semibold uppercase tracking-[0.06em] text-[var(--txt-muted)] border-b border-[var(--border)]">Vehicles</th>
                <th className="text-left px-5 py-2.5 text-[11px] font-semibold uppercase tracking-[0.06em] text-[var(--txt-muted)] border-b border-[var(--border)]">Avg Speed</th>
                <th className="text-left px-5 py-2.5 text-[11px] font-semibold uppercase tracking-[0.06em] text-[var(--txt-muted)] border-b border-[var(--border)]">Congestion</th>
                <th className="text-left px-5 py-2.5 text-[11px] font-semibold uppercase tracking-[0.06em] text-[var(--txt-muted)] border-b border-[var(--border)]">Green Time</th>
              </tr>
            </thead>
            <tbody>
              {dirs.map((d) => (
                <tr key={d} className="hover:bg-[var(--bg-card-hover)] transition-colors">
                  <td className="px-5 py-3 capitalize font-medium text-[var(--txt)]">{d}</td>
                  <td className="px-5 py-3 text-[var(--txt-secondary)]" style={{ fontFamily: 'var(--font-mono)' }}>{j.traffic[d].vehicle_count}</td>
                  <td className="px-5 py-3 text-[var(--txt-secondary)]" style={{ fontFamily: 'var(--font-mono)' }}>{j.traffic[d].avg_speed} km/h</td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-[var(--bg-surface)] rounded-full overflow-hidden">
                        <div className="h-full rounded-full" style={{ width: `${j.congestion[d] * 100}%`, background: congestionColor(j.congestion[d]) }} />
                      </div>
                      <span className="font-semibold" style={{ color: congestionColor(j.congestion[d]), fontFamily: 'var(--font-mono)' }}>
                        {(j.congestion[d] * 100).toFixed(1)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-5 py-3">
                    <span className="text-[var(--success)] font-semibold" style={{ fontFamily: 'var(--font-mono)' }}>{j.green_times[d]}s</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default function SimulationPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const toast = useToast()

  async function runSimulation() {
    setLoading(true)
    try {
      const { data: res } = await api.post('/simulate')
      setData(res)
      toast('Simulation completed')
    } catch (err) {
      toast(err.response?.data?.detail || 'Simulation failed', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="animate-in">
      <PageHeader title="Detailed Simulation Results">
        <button
          onClick={runSimulation}
          disabled={loading}
          className="flex items-center gap-2 px-5 py-2.5 bg-[var(--accent)] text-[var(--bg-deep)] font-semibold text-[13px] rounded-lg hover:shadow-lg hover:shadow-[var(--accent-glow)] transition-all active:scale-[0.98] disabled:opacity-50"
        >
          <Play size={14} />
          {loading ? 'Running...' : 'Run Simulation'}
        </button>
      </PageHeader>

      {data ? (
        <div className="flex flex-col gap-3">
          {/* Summary bar */}
          <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-4 mb-2 flex items-center gap-8 text-[13px]">
            <div>
              <span className="text-[var(--txt-muted)]">Average: </span>
              <span className="font-bold" style={{ fontFamily: 'var(--font-mono)', color: congestionColor(data.analysis.avg_congestion) }}>
                {(data.analysis.avg_congestion * 100).toFixed(1)}%
              </span>
            </div>
            <div>
              <span className="text-[var(--txt-muted)]">Critical: </span>
              <span className="font-bold text-[var(--danger)]" style={{ fontFamily: 'var(--font-mono)' }}>
                {data.analysis.critical_junction} ({(data.analysis.critical_congestion * 100).toFixed(1)}%)
              </span>
            </div>
            <div>
              <span className="text-[var(--txt-muted)]">Least: </span>
              <span className="font-bold text-[var(--success)]" style={{ fontFamily: 'var(--font-mono)' }}>
                {data.analysis.least_congested} ({(data.analysis.least_congestion * 100).toFixed(1)}%)
              </span>
            </div>
          </div>

          {data.junctions.map((j, i) => (
            <JunctionTable key={j.junction_id} junction={j} defaultOpen={i === 0} />
          ))}
        </div>
      ) : (
        <EmptyState icon={Clock} message="Run a simulation to see detailed results" />
      )}
    </div>
  )
}
