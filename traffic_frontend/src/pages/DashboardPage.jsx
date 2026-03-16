import { useState } from 'react'
import { Play, Clock, AlertTriangle, Shield, Zap } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { StatCard, CongestionBadge, congestionColor, EmptyState, PageHeader } from '../components/UI'
import { useToast } from '../components/UI'
import api from '../lib/api'

export default function DashboardPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [simCount, setSimCount] = useState(0)
  const toast = useToast()

  async function runSimulation() {
    setLoading(true)
    try {
      const { data: res } = await api.post('/simulate')
      setData(res)
      setSimCount((c) => c + 1)
      toast('Simulation completed')
    } catch (err) {
      toast(err.response?.data?.detail || 'Simulation failed', 'error')
    } finally {
      setLoading(false)
    }
  }

  const analysis = data?.analysis
  const chartData = data?.junctions.map((j) => ({
    name: j.junction_id,
    congestion: +(j.total_congestion * 100).toFixed(1),
  }))

  return (
    <div className="animate-in">
      <PageHeader title="Traffic Overview">
        <button
          onClick={runSimulation}
          disabled={loading}
          className="flex items-center gap-2 px-5 py-2.5 bg-[var(--accent)] text-[var(--bg-deep)] font-semibold text-[13px] rounded-lg hover:shadow-lg hover:shadow-[var(--accent-glow)] transition-all active:scale-[0.98] disabled:opacity-50"
        >
          <Play size={14} />
          {loading ? 'Running...' : 'Run Simulation'}
        </button>
      </PageHeader>

      {/* Stats Row */}
      <div className="grid grid-cols-4 gap-4 mb-7">
        <StatCard
          label="Avg Congestion"
          value={analysis ? `${(analysis.avg_congestion * 100).toFixed(1)}%` : '—'}
          sub="Across 9 junctions"
          color="cyan"
        />
        <StatCard
          label="Critical Junction"
          value={analysis?.critical_junction || '—'}
          sub={analysis ? `Congestion: ${(analysis.critical_congestion * 100).toFixed(1)}%` : ''}
          color="red"
        />
        <StatCard
          label="Least Congested"
          value={analysis?.least_congested || '—'}
          sub={analysis ? `Congestion: ${(analysis.least_congestion * 100).toFixed(1)}%` : ''}
          color="green"
        />
        <StatCard label="Simulations" value={simCount} sub="This session" color="amber" />
      </div>

      {/* Congestion Chart */}
      {chartData && (
        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-5 mb-7">
          <h4 className="text-[13px] font-semibold text-[var(--txt-secondary)] mb-4">Congestion by Junction (%)</h4>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} barSize={32} margin={{ top: 5, right: 10, bottom: 0, left: -10 }}>
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} domain={[0, 100]} />
              <Tooltip
                contentStyle={{ background: '#111827', border: '1px solid rgba(148,163,184,0.15)', borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: '#f1f5f9', fontWeight: 600 }}
                itemStyle={{ color: '#94a3b8' }}
                formatter={(v) => [`${v}%`, 'Congestion']}
              />
              <Bar dataKey="congestion" radius={[6, 6, 0, 0]}>
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.congestion < 30 ? '#10b981' : entry.congestion < 60 ? '#f59e0b' : '#f43f5e'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Junction Grid */}
      {data ? (
        <div className="grid grid-cols-3 gap-4">
          {data.junctions.map((j, idx) => {
            const pct = (j.total_congestion * 100).toFixed(1)
            return (
              <div
                key={j.junction_id}
                className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-4 hover:border-[var(--border-hover)] hover:shadow-lg hover:shadow-black/20 transition-all animate-in"
                style={{ animationDelay: `${idx * 40}ms` }}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-[15px] font-bold" style={{ fontFamily: 'var(--font-mono)' }}>{j.junction_id}</span>
                  <CongestionBadge value={j.total_congestion} />
                </div>
                <div className="flex items-baseline justify-between mb-2">
                  <span className="text-[22px] font-bold" style={{ fontFamily: 'var(--font-mono)' }}>{pct}%</span>
                  <span className="text-[11px] text-[var(--txt-muted)]">congestion</span>
                </div>
                {/* Bar */}
                <div className="h-1.5 bg-[var(--bg-surface)] rounded-full overflow-hidden mb-3">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{ width: `${pct}%`, background: congestionColor(j.total_congestion) }}
                  />
                </div>
                {/* Direction breakdown */}
                <div className="grid grid-cols-2 gap-1.5">
                  {['north', 'south', 'east', 'west'].map((d) => (
                    <div key={d} className="flex items-center justify-between bg-[var(--bg-surface)] rounded-md px-2.5 py-1.5 text-[11px]">
                      <span className="text-[var(--txt-muted)] capitalize font-medium">{d}</span>
                      <span className="text-[var(--success)] font-semibold" style={{ fontFamily: 'var(--font-mono)' }}>{j.green_times[d]}s</span>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <EmptyState icon={Clock} message="Run a simulation to see junction data" />
      )}
    </div>
  )
}
