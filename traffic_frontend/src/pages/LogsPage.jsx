import { useState, useEffect } from 'react'
import { Loader, RefreshCw, FileText } from 'lucide-react'
import { congestionColor, EmptyState, PageHeader, useToast } from '../components/UI'
import api from '../lib/api'

export default function LogsPage() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const toast = useToast()

  async function loadLogs() {
    setLoading(true)
    try {
      const { data } = await api.get('/admin/logs?limit=50')
      setLogs(data)
    } catch (err) {
      toast(err.response?.data?.detail || 'Failed to load logs', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadLogs() }, [])

  return (
    <div className="animate-in">
      <PageHeader title="Simulation Logs">
        <button
          onClick={loadLogs}
          className="flex items-center gap-2 px-4 py-2 text-[13px] font-medium text-[var(--txt-secondary)] border border-[var(--border-hover)] rounded-lg hover:border-[var(--accent)] hover:text-[var(--accent)] transition-all"
        >
          <RefreshCw size={14} /> Refresh
        </button>
      </PageHeader>

      {loading ? (
        <div className="flex items-center justify-center py-20 text-[var(--txt-muted)]">
          <Loader size={20} className="animate-spin mr-3" /> Loading logs...
        </div>
      ) : logs.length === 0 ? (
        <EmptyState icon={FileText} message="No logs yet. Run a simulation first." />
      ) : (
        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl overflow-hidden">
          <div className="px-5 py-3.5 border-b border-[var(--border)] flex items-center justify-between">
            <h3 className="text-[14px] font-semibold">Recent Simulation Logs</h3>
            <span className="text-[12px] text-[var(--txt-muted)]">{logs.length} entries</span>
          </div>
          <table className="w-full text-[13px]">
            <thead>
              <tr>
                {['#', 'Timestamp', 'Avg Congestion', 'Critical Junction', 'Critical Congestion'].map((h) => (
                  <th key={h} className="text-left px-5 py-2.5 text-[11px] font-semibold uppercase tracking-[0.06em] text-[var(--txt-muted)] border-b border-[var(--border)]">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {logs.map((l, i) => (
                <tr key={i} className="hover:bg-[var(--bg-card-hover)] transition-colors animate-in" style={{ animationDelay: `${i * 20}ms` }}>
                  <td className="px-5 py-3 text-[var(--txt-muted)]" style={{ fontFamily: 'var(--font-mono)' }}>{i + 1}</td>
                  <td className="px-5 py-3 text-[var(--txt-secondary)]" style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>
                    {new Date(l.timestamp).toLocaleString()}
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-12 h-1.5 bg-[var(--bg-surface)] rounded-full overflow-hidden">
                        <div className="h-full rounded-full" style={{ width: `${l.avg_congestion * 100}%`, background: congestionColor(l.avg_congestion) }} />
                      </div>
                      <span className="font-semibold" style={{ color: congestionColor(l.avg_congestion), fontFamily: 'var(--font-mono)' }}>
                        {(l.avg_congestion * 100).toFixed(1)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-5 py-3 font-semibold text-[var(--txt)]">{l.critical_junction}</td>
                  <td className="px-5 py-3">
                    <span className="font-semibold text-[var(--danger)]" style={{ fontFamily: 'var(--font-mono)' }}>
                      {(l.critical_congestion * 100).toFixed(1)}%
                    </span>
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
