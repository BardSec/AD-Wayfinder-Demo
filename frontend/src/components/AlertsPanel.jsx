import { useEffect, useState, useMemo } from 'react'
import { AlertTriangle, User, ArrowUpDown, Filter, Loader2,
         Clock, Calendar, Building2, ChevronRight } from 'lucide-react'
import { api } from '../api/adApi'

const SORT_FIELDS = [
  { key: 'days_since_login', label: 'Days Since Login' },
  { key: 'name', label: 'Name' },
  { key: 'department', label: 'Department' },
  { key: 'ou', label: 'OU' },
]

export default function AlertsPanel({ onUserSelect }) {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [sortField, setSortField] = useState('days_since_login')
  const [sortAsc, setSortAsc] = useState(false)
  const [filterOU, setFilterOU] = useState('all')
  const [filterType, setFilterType] = useState('all')  // 'all' | 'never' | 'stale'

  useEffect(() => {
    api.getAlerts()
      .then(setAlerts)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const ous = useMemo(() => {
    const set = new Set(alerts.map((a) => a.ou).filter(Boolean))
    return ['all', ...Array.from(set).sort()]
  }, [alerts])

  const filtered = useMemo(() => {
    let list = alerts
    if (filterOU !== 'all') list = list.filter((a) => a.ou === filterOU)
    if (filterType === 'never') list = list.filter((a) => a.never_logged_in)
    if (filterType === 'stale') list = list.filter((a) => !a.never_logged_in)
    list = [...list].sort((a, b) => {
      let av = a[sortField] ?? (sortField === 'days_since_login' ? 999999 : '')
      let bv = b[sortField] ?? (sortField === 'days_since_login' ? 999999 : '')
      if (typeof av === 'string') av = av.toLowerCase()
      if (typeof bv === 'string') bv = bv.toLowerCase()
      return sortAsc ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1)
    })
    return list
  }, [alerts, filterOU, filterType, sortField, sortAsc])

  const toggleSort = (field) => {
    if (sortField === field) setSortAsc((a) => !a)
    else { setSortField(field); setSortAsc(false) }
  }

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
      {/* ── Toolbar ── */}
      <div className="flex-shrink-0 bg-white border-b border-slate-200 px-6 py-3 flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <AlertTriangle size={16} className="text-red-500" />
          <span className="font-semibold text-slate-800">
            {filtered.length} alert{filtered.length !== 1 ? 's' : ''}
          </span>
          {filtered.length < alerts.length && (
            <span className="text-slate-400 text-sm">of {alerts.length} total</span>
          )}
        </div>

        <div className="flex items-center gap-2 ml-auto flex-wrap">
          <Filter size={14} className="text-slate-400" />

          {/* Type filter */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="text-sm border border-slate-200 rounded-lg px-2 py-1.5 bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-400"
          >
            <option value="all">All alert types</option>
            <option value="never">Never logged in</option>
            <option value="stale">Old last login</option>
          </select>

          {/* OU filter */}
          <select
            value={filterOU}
            onChange={(e) => setFilterOU(e.target.value)}
            className="text-sm border border-slate-200 rounded-lg px-2 py-1.5 bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-400"
          >
            {ous.map((ou) => (
              <option key={ou} value={ou}>{ou === 'all' ? 'All OUs' : ou}</option>
            ))}
          </select>
        </div>
      </div>

      {/* ── Table ── */}
      <div className="flex-1 overflow-auto">
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-3">
            <AlertTriangle size={36} className="text-slate-300" />
            <p className="font-medium">No alerts match your filters</p>
          </div>
        ) : (
          <table className="w-full text-sm border-collapse">
            <thead className="sticky top-0 bg-slate-50 border-b border-slate-200 z-10">
              <tr>
                <Th>User</Th>
                <SortTh field="days_since_login" sortField={sortField} sortAsc={sortAsc} onSort={toggleSort}>
                  Last Login
                </SortTh>
                <SortTh field="department" sortField={sortField} sortAsc={sortAsc} onSort={toggleSort}>
                  Department
                </SortTh>
                <SortTh field="ou" sortField={sortField} sortAsc={sortAsc} onSort={toggleSort}>
                  OU
                </SortTh>
                <Th>Severity</Th>
                <Th />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((alert) => (
                <tr
                  key={alert.dn}
                  onClick={() => onUserSelect({ type: 'user', dn: alert.dn, name: alert.name })}
                  className="hover:bg-red-50/40 cursor-pointer transition-colors group"
                >
                  {/* User */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                        <User size={13} className="text-red-500" />
                      </div>
                      <div>
                        <div className="font-medium text-slate-800">{alert.name}</div>
                        {alert.sam && (
                          <div className="text-xs text-slate-400 font-mono">{alert.sam}</div>
                        )}
                        {alert.email && (
                          <div className="text-xs text-slate-400">{alert.email}</div>
                        )}
                      </div>
                    </div>
                  </td>

                  {/* Last login */}
                  <td className="px-4 py-3">
                    {alert.never_logged_in ? (
                      <span className="inline-flex items-center gap-1 bg-red-100 text-red-700 text-xs font-semibold px-2 py-1 rounded-full">
                        <Calendar size={11} /> Never
                      </span>
                    ) : (
                      <div>
                        <div className="flex items-center gap-1 text-slate-700">
                          <Clock size={12} className="text-slate-400" />
                          {fmtDate(alert.last_logon)}
                        </div>
                        <div className="text-xs text-red-600 font-semibold mt-0.5">
                          {alert.days_since_login} days ago
                        </div>
                      </div>
                    )}
                  </td>

                  {/* Department */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1.5 text-slate-600">
                      <Building2 size={12} className="text-slate-400" />
                      {alert.department || <span className="text-slate-300">—</span>}
                    </div>
                  </td>

                  {/* OU */}
                  <td className="px-4 py-3 text-slate-600 text-xs">{alert.ou || '—'}</td>

                  {/* Severity */}
                  <td className="px-4 py-3">
                    <SeverityBadge alert={alert} />
                  </td>

                  {/* Action */}
                  <td className="px-4 py-3 text-right">
                    <ChevronRight size={16} className="text-slate-300 group-hover:text-indigo-400 transition-colors ml-auto" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

// ── Table header cells ─────────────────────────────────────────────────────────

function Th({ children }) {
  return (
    <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">
      {children}
    </th>
  )
}

function SortTh({ field, children, sortField, sortAsc, onSort }) {
  const active = sortField === field
  return (
    <th
      onClick={() => onSort(field)}
      className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide cursor-pointer hover:text-slate-700 select-none"
    >
      <span className="flex items-center gap-1">
        {children}
        <ArrowUpDown
          size={11}
          className={active ? 'text-indigo-500' : 'text-slate-300'}
        />
      </span>
    </th>
  )
}

// ── Severity badge ─────────────────────────────────────────────────────────────

function SeverityBadge({ alert }) {
  if (alert.never_logged_in) {
    return (
      <span className="inline-flex items-center gap-1 bg-red-100 text-red-700 text-xs font-semibold px-2 py-0.5 rounded-full">
        <AlertTriangle size={10} /> Never logged in
      </span>
    )
  }
  if (alert.days_since_login > 365) {
    return (
      <span className="inline-flex items-center gap-1 bg-red-100 text-red-700 text-xs font-semibold px-2 py-0.5 rounded-full">
        <AlertTriangle size={10} /> Critical
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1 bg-amber-100 text-amber-700 text-xs font-semibold px-2 py-0.5 rounded-full">
      <AlertTriangle size={10} /> Warning
    </span>
  )
}

function fmtDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}
