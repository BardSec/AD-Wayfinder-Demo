import { useEffect, useState } from 'react'
import { UserPlus, Mail, Phone, Folder, Users, CheckCircle2,
         XCircle, Loader2, ChevronRight, AlertCircle } from 'lucide-react'
import { api } from '../api/adApi'

// ── Avatar helpers ─────────────────────────────────────────────────────────────
const AVATAR_COLORS = [
  'bg-indigo-500', 'bg-emerald-500', 'bg-amber-500',
  'bg-violet-500', 'bg-rose-500', 'bg-sky-500',
]

function avatarColor(name = '') {
  return AVATAR_COLORS[name.charCodeAt(0) % AVATAR_COLORS.length]
}

function initials(name = '') {
  return name.split(' ').slice(0, 2).map((s) => s[0] ?? '').join('').toUpperCase()
}

// ── Main component ─────────────────────────────────────────────────────────────
export default function NewTodayPanel({ onUserSelect }) {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getNewToday()
      .then(setUsers)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  })

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <Loader2 size={28} className="animate-spin text-indigo-500" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700 text-sm">{error}</div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* ── Header ── */}
      <div className="flex-shrink-0 bg-white border-b border-slate-200 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-100 flex items-center justify-center">
            <UserPlus size={18} className="text-emerald-600" />
          </div>
          <div>
            <h2 className="font-bold text-slate-800 text-base leading-tight">
              New Accounts Today
              {users.length > 0 && (
                <span className="ml-2 bg-emerald-100 text-emerald-700 text-sm font-semibold px-2 py-0.5 rounded-full">
                  {users.length}
                </span>
              )}
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">{today}</p>
          </div>
        </div>
        {users.length > 0 && (
          <p className="text-sm text-slate-500 mt-3">
            Accounts provisioned today. Use this panel to verify onboarding steps
            are complete before end of day.
          </p>
        )}
      </div>

      {/* ── Content ── */}
      <div className="flex-1 overflow-y-auto p-6">
        {users.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {users.map((user) => (
              <UserCard key={user.dn} user={user} onSelect={onUserSelect} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// ── Individual user card ───────────────────────────────────────────────────────
function UserCard({ user, onSelect }) {
  const checks = [
    {
      label: 'Account enabled',
      ok: user.enabled,
      failMsg: 'Account is disabled',
    },
    {
      label: 'Email configured',
      ok: user.has_email,
      failMsg: 'No email address set',
    },
    {
      label: 'First login completed',
      ok: user.has_logged_in,
      failMsg: 'Has not logged in yet',
    },
    {
      label: 'Group membership set',
      ok: user.group_count > 0,
      failMsg: 'No group memberships',
    },
  ]

  const pendingCount = checks.filter((c) => !c.ok).length

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow flex flex-col overflow-hidden">
      {/* Card header */}
      <div className="px-4 pt-4 pb-3 flex items-start gap-3">
        <div className={`w-11 h-11 rounded-full ${avatarColor(user.name)} flex items-center justify-center text-white font-bold text-sm flex-shrink-0`}>
          {initials(user.name)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-slate-800 truncate leading-tight">{user.name}</div>
          {user.title && (
            <div className="text-xs text-slate-500 truncate mt-0.5">{user.title}</div>
          )}
          {user.department && (
            <div className="text-xs text-slate-400 truncate">{user.department}</div>
          )}
        </div>
        {pendingCount > 0 && (
          <span className="flex-shrink-0 bg-amber-100 text-amber-700 text-xs font-semibold px-1.5 py-0.5 rounded-full">
            {pendingCount} pending
          </span>
        )}
      </div>

      {/* Meta */}
      <div className="px-4 pb-3 space-y-1.5 border-b border-slate-100">
        {user.email && (
          <MetaRow icon={<Mail size={12} />} value={user.email} />
        )}
        {user.phone && (
          <MetaRow icon={<Phone size={12} />} value={user.phone} />
        )}
        <MetaRow
          icon={<Folder size={12} className="text-amber-500" />}
          value={user.ou_name || '—'}
        />
        {user.group_count > 0 && (
          <MetaRow
            icon={<Users size={12} className="text-emerald-500" />}
            value={user.groups.map((g) => g.name).join(', ')}
          />
        )}
      </div>

      {/* Onboarding checklist */}
      <div className="px-4 py-3 flex-1">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
          Onboarding Checklist
        </p>
        <ul className="space-y-1.5">
          {checks.map((c) => (
            <li key={c.label} className="flex items-center gap-2">
              {c.ok ? (
                <CheckCircle2 size={14} className="text-emerald-500 flex-shrink-0" />
              ) : (
                <XCircle size={14} className="text-red-400 flex-shrink-0" />
              )}
              <span className={`text-xs ${c.ok ? 'text-slate-600' : 'text-red-600 font-medium'}`}>
                {c.ok ? c.label : c.failMsg}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Footer action */}
      <div className="px-4 pb-4">
        <button
          onClick={() => onSelect({ type: 'user', dn: user.dn, name: user.name })}
          className="w-full flex items-center justify-center gap-1.5 bg-slate-50 hover:bg-indigo-50 text-slate-600 hover:text-indigo-700 border border-slate-200 hover:border-indigo-200 rounded-lg py-2 text-sm font-medium transition-colors"
        >
          View Full Profile
          <ChevronRight size={14} />
        </button>
      </div>
    </div>
  )
}

function MetaRow({ icon, value }) {
  return (
    <div className="flex items-center gap-1.5 text-xs text-slate-500 truncate">
      <span className="flex-shrink-0 text-slate-400">{icon}</span>
      <span className="truncate">{value}</span>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-slate-400 gap-4">
      <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center">
        <UserPlus size={28} className="text-slate-300" />
      </div>
      <div className="text-center">
        <p className="font-semibold text-slate-500">No new accounts today</p>
        <p className="text-sm mt-1">
          Accounts created today will appear here automatically.
        </p>
        <p className="text-xs mt-3 flex items-center gap-1 justify-center text-slate-400">
          <AlertCircle size={12} />
          Data refreshes every 15 minutes — use the refresh button to check immediately
        </p>
      </div>
    </div>
  )
}
