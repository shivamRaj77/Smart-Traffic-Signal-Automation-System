import { useState, useEffect, createContext, useContext, useCallback } from 'react'

/* ── Stat Card ── */
export function StatCard({ label, value, sub, color = 'cyan', className = '' }) {
  const colors = {
    cyan: 'var(--accent)',
    red: 'var(--danger)',
    amber: 'var(--warn)',
    green: 'var(--success)',
  }
  return (
    <div className={`relative overflow-hidden bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-5 transition-all duration-200 hover:border-[var(--border-hover)] hover:-translate-y-0.5 hover:shadow-lg hover:shadow-black/30 group ${className}`}>
      <div className="absolute top-0 left-0 right-0 h-0.5 opacity-0 group-hover:opacity-100 transition-opacity" style={{ background: colors[color] }} />
      <p className="text-[12px] text-[var(--txt-muted)] font-medium uppercase tracking-[0.05em]">{label}</p>
      <p className="text-[28px] font-bold mt-1 tracking-tight font-[var(--font-mono)]" style={{ fontFamily: 'var(--font-mono)' }}>{value}</p>
      {sub && <p className="text-[12px] text-[var(--txt-secondary)] mt-1">{sub}</p>}
    </div>
  )
}

/* ── Congestion Badge ── */
export function CongestionBadge({ value }) {
  if (value < 0.3)
    return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[var(--success-dim)] text-[var(--success)]">Low</span>
  if (value < 0.6)
    return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[var(--warn-dim)] text-[var(--warn)]">Moderate</span>
  return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[var(--danger-dim)] text-[var(--danger)]">High</span>
}

/* ── Congestion Color ── */
export function congestionColor(v) {
  if (v < 0.3) return 'var(--success)'
  if (v < 0.6) return 'var(--warn)'
  return 'var(--danger)'
}

/* ── Empty State ── */
export function EmptyState({ icon: Icon, message }) {
  return (
    <div className="text-center py-16 text-[var(--txt-muted)]">
      {Icon && <Icon size={44} className="mx-auto mb-3 opacity-40" />}
      <p className="text-[14px]">{message}</p>
    </div>
  )
}

/* ── Page Header with action ── */
export function PageHeader({ title, children }) {
  return (
    <div className="flex items-center justify-between mb-6">
      <h3 className="text-[14px] font-semibold flex items-center gap-2 before:content-[''] before:w-[3px] before:h-4 before:rounded before:bg-[var(--accent)]">{title}</h3>
      {children}
    </div>
  )
}

/* ── Toast System ── */
const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toast, setToast] = useState(null)

  const showToast = useCallback((msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3000)
  }, [])

  return (
    <ToastContext.Provider value={showToast}>
      {children}
      {toast && (
        <div className={`fixed bottom-6 right-6 px-5 py-3 rounded-lg text-[13px] font-medium z-[2000] text-white animate-in ${
          toast.type === 'success' ? 'bg-[var(--success)]' : 'bg-[var(--danger)]'
        }`}>
          {toast.msg}
        </div>
      )}
    </ToastContext.Provider>
  )
}

export const useToast = () => useContext(ToastContext)
