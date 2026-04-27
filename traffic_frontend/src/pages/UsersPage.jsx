import { useState, useEffect } from 'react'
import { Trash2, Shield, User, Loader, RefreshCw } from 'lucide-react'
import { PageHeader, useToast } from '../components/UI'
import api from '../lib/api'

export default function UsersPage() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const toast = useToast()

  async function loadUsers() {
    setLoading(true)
    try {
      const { data } = await api.get('/admin/users')
      setUsers(data)
    } catch (err) {
      toast(err.response?.data?.detail || 'Failed to load users', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadUsers() }, [])

  async function deleteUser(id, name) {
    if (!window.confirm(`Delete user "${name}"?`)) return
    try {
      await api.delete(`/admin/users/${id}`)
      toast(`User "${name}" deleted`)
      loadUsers()
    } catch (err) {
      toast(err.response?.data?.detail || 'Delete failed', 'error')
    }
  }

  return (
    <div className="animate-in">
      <PageHeader title="User Management">
        <button
          onClick={loadUsers}
          className="flex items-center gap-2 px-4 py-2 text-[13px] font-medium text-[var(--txt-secondary)] border border-[var(--border-hover)] rounded-lg hover:border-[var(--accent)] hover:text-[var(--accent)] transition-all"
        >
          <RefreshCw size={14} />
          Refresh
        </button>
      </PageHeader>

      {loading ? (
        <div className="flex items-center justify-center py-20 text-[var(--txt-muted)]">
          <Loader size={20} className="animate-spin mr-3" /> Loading users...
        </div>
      ) : (
        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl overflow-hidden">
          <div className="px-5 py-3.5 border-b border-[var(--border)] flex items-center justify-between">
            <h3 className="text-[14px] font-semibold">{users.length} Registered Users</h3>
          </div>
          <table className="w-full text-[13px]">
            <thead>
              <tr>
                <th className="text-left px-5 py-2.5 text-[11px] font-semibold uppercase tracking-[0.06em] text-[var(--txt-muted)] border-b border-[var(--border)]">ID</th>
                <th className="text-left px-5 py-2.5 text-[11px] font-semibold uppercase tracking-[0.06em] text-[var(--txt-muted)] border-b border-[var(--border)]">Username</th>
                <th className="text-left px-5 py-2.5 text-[11px] font-semibold uppercase tracking-[0.06em] text-[var(--txt-muted)] border-b border-[var(--border)]">Role</th>
                <th className="text-left px-5 py-2.5 text-[11px] font-semibold uppercase tracking-[0.06em] text-[var(--txt-muted)] border-b border-[var(--border)]">Created</th>
                <th className="text-right px-5 py-2.5 text-[11px] font-semibold uppercase tracking-[0.06em] text-[var(--txt-muted)] border-b border-[var(--border)]">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u, i) => (
                <tr key={u.id} className="hover:bg-[var(--bg-card-hover)] transition-colors animate-in" style={{ animationDelay: `${i * 30}ms` }}>
                  <td className="px-5 py-3">
                    <code className="text-[11px] text-[var(--txt-muted)]" style={{ fontFamily: 'var(--font-mono)' }}>{u.id}</code>
                  </td>
                  <td className="px-5 py-3 font-medium text-[var(--txt)]">{u.username}</td>
                  <td className="px-5 py-3">
                    {u.role === 'admin' ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[var(--accent-dim)] text-[var(--accent)]">
                        <Shield size={11} /> Admin
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[var(--success-dim)] text-[var(--success)]">
                        <User size={11} /> User
                      </span>
                    )}
                  </td>
                  <td className="px-5 py-3 text-[var(--txt-secondary)]">{new Date(u.created_at).toLocaleDateString()}</td>
                  <td className="px-5 py-3 text-right">
                    <button
                      onClick={() => deleteUser(u.id, u.username)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-[12px] font-semibold text-[var(--danger)] bg-[var(--danger-dim)] rounded-lg hover:bg-[var(--danger)] hover:text-white transition-all"
                    >
                      <Trash2 size={12} /> Delete
                    </button>
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
