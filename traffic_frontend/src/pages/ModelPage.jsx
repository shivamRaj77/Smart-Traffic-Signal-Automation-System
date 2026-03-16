import { useState, useEffect } from 'react'
import { Cpu, GitBranch, Database, Tag, Hash, Loader } from 'lucide-react'
import { PageHeader } from '../components/UI'
import api from '../lib/api'

const iconMap = {
  model_type: Cpu,
  features: GitBranch,
  target: Database,
  version: Tag,
  training_samples: Hash,
}

export default function ModelPage() {
  const [info, setInfo] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/model/info')
      .then(({ data }) => setInfo(data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-[var(--txt-muted)]">
        <Loader size={20} className="animate-spin mr-3" /> Loading model info...
      </div>
    )
  }

  return (
    <div className="animate-in">
      <PageHeader title="ML Prediction Model" />

      {/* Hero card */}
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-6 mb-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-xl bg-[var(--accent-dim)] flex items-center justify-center">
            <Cpu size={22} className="text-[var(--accent)]" />
          </div>
          <div>
            <h3 className="text-[18px] font-bold">{info?.model_type || 'Unknown'}</h3>
            <p className="text-[13px] text-[var(--txt-secondary)]">Congestion prediction engine</p>
          </div>
        </div>
        <p className="text-[13px] text-[var(--txt-secondary)] leading-relaxed">
          This model predicts traffic congestion levels for each direction at every junction using real-time
          traffic features. The predicted congestion scores are normalized between 0 and 1, then used to
          proportionally allocate green signal timings across all directions.
        </p>
      </div>

      {/* Detail cards */}
      <div className="grid grid-cols-2 gap-4">
        {info && Object.entries(info).map(([key, value], idx) => {
          const Icon = iconMap[key] || Hash
          return (
            <div
              key={key}
              className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-5 hover:border-[var(--border-hover)] transition-all animate-in"
              style={{ animationDelay: `${idx * 60}ms` }}
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 rounded-lg bg-[var(--accent-dim)] flex items-center justify-center">
                  <Icon size={15} className="text-[var(--accent)]" />
                </div>
                <span className="text-[12px] font-semibold uppercase tracking-[0.06em] text-[var(--txt-muted)]">
                  {key.replace(/_/g, ' ')}
                </span>
              </div>
              <p className="text-[14px] font-semibold break-words" style={{ fontFamily: 'var(--font-mono)' }}>{value}</p>
            </div>
          )
        })}
      </div>

      {/* Formula explanation */}
      <div className="mt-6 bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-6">
        <h4 className="text-[13px] font-semibold text-[var(--txt-secondary)] mb-3">How it works</h4>
        <div className="space-y-3 text-[13px] text-[var(--txt-secondary)] leading-relaxed">
          <div className="flex gap-3">
            <span className="w-6 h-6 rounded-md bg-[var(--accent-dim)] text-[var(--accent)] flex items-center justify-center text-[11px] font-bold flex-shrink-0">1</span>
            <p>Synthetic traffic data is generated for each junction direction: vehicle count and average speed.</p>
          </div>
          <div className="flex gap-3">
            <span className="w-6 h-6 rounded-md bg-[var(--accent-dim)] text-[var(--accent)] flex items-center justify-center text-[11px] font-bold flex-shrink-0">2</span>
            <p>The Ridge Regression model predicts raw congestion from these features, then normalizes scores to 0–1.</p>
          </div>
          <div className="flex gap-3">
            <span className="w-6 h-6 rounded-md bg-[var(--accent-dim)] text-[var(--accent)] flex items-center justify-center text-[11px] font-bold flex-shrink-0">3</span>
            <p>Green signal time is distributed proportionally to congestion share within a 120-second cycle, with a 10-second minimum per direction.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
