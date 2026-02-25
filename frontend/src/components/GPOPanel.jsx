import { useState, useEffect } from 'react'
import { ShieldCheck, ShieldAlert, ShieldOff, Search, Lock,
         Loader2, AlertTriangle, Calendar, Link, X, ChevronRight,
         Folder } from 'lucide-react'
import { api } from '../api/adApi'

export default function GPOPanel() {
  const [gpos, setGpos] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('')
  const [selected, setSelected] = useState(null)
  const [detail, setDetail] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)

  useEffect(() => {
    api.getGPOs()
      .then(setGpos)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const selectGPO = (gpo) => {
    setSelected(gpo)
    setDetail(null)
    setDetailLoading(true)
    api.getGPO(gpo.guid)
      .then(setDetail)
      .catch(() => setDetail({ error: 'Failed to load GPO details' }))
      .finally(() => setDetailLoading(false))
  }

  const filtered = (gpos || []).filter((g) =>
    !filter ||
    g.name.toLowerCase().includes(filter.toLowerCase()) ||
    (g.description || '').toLowerCase().includes(filter.toLowerCase())
  )

  return (
    <div className="flex-1 flex overflow-hidden bg-slate-50">
      {/* Left: GPO inventory list */}
      <div className="w-96 flex-shrink-0 bg-white border-r border-slate-200 flex flex-col overflow-hidden">
        {/* List header */}
        <div className="flex-shrink-0 px-4 py-3 border-b border-slate-200 space-y-2">
          <div className="flex items-center gap-2">
            <ShieldCheck size={16} className="text-indigo-500" />
            <span className="font-semibold text-slate-800 text-sm">GPO Inventory</span>
            {gpos && (
              <span className="ml-auto text-xs text-slate-400">{gpos.length} policies</span>
            )}
          </div>
          <div className="relative">
            <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            <input
              type="text"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="Filter policies…"
              className="w-full bg-slate-50 text-slate-800 placeholder-slate-400 text-sm rounded-md pl-8 pr-7 py-1.5 border border-slate-200 focus:outline-none focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400"
            />
            {filter && (
              <button
                onClick={() => setFilter('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <X size={12} />
              </button>
            )}
          </div>
        </div>

        {/* List body */}
        <div className="flex-1 overflow-y-auto">
          {loading && (
            <div className="flex items-center justify-center h-32 text-slate-400">
              <Loader2 size={20} className="animate-spin" />
            </div>
          )}
          {error && (
            <div className="p-4 flex items-start gap-2 text-red-600 text-sm">
              <AlertTriangle size={14} className="flex-shrink-0 mt-0.5" />
              {error}
            </div>
          )}
          {!loading && !error && filtered.length === 0 && (
            <p className="px-4 py-6 text-center text-slate-400 text-sm">No policies found</p>
          )}
          {filtered.map((g) => (
            <button
              key={g.guid}
              onClick={() => selectGPO(g)}
              className={`w-full flex items-start gap-3 px-4 py-3 text-left border-b border-slate-50 transition-colors ${
                selected?.guid === g.guid
                  ? 'bg-indigo-50 border-l-2 border-l-indigo-500'
                  : 'hover:bg-slate-50'
              }`}
            >
              <span className="flex-shrink-0 mt-0.5">
                <StatusIcon status={g.status} size={14} />
              </span>
              <span className="flex-1 min-w-0">
                <span className="text-sm font-medium text-slate-800 truncate block">{g.name}</span>
                {g.description && (
                  <span className="text-xs text-slate-400 truncate block mt-0.5 leading-tight">
                    {g.description}
                  </span>
                )}
                <span className="flex items-center gap-2 mt-1 text-xs text-slate-400">
                  <span className="flex items-center gap-0.5">
                    <Link size={10} />
                    {g.link_count} link{g.link_count !== 1 ? 's' : ''}
                  </span>
                  {g.when_changed && (
                    <span className="flex items-center gap-0.5">
                      <Calendar size={10} />
                      {g.when_changed.split('T')[0]}
                    </span>
                  )}
                </span>
              </span>
              <ChevronRight size={14} className="text-slate-300 flex-shrink-0 mt-1" />
            </button>
          ))}
        </div>
      </div>

      {/* Right: GPO detail */}
      <div className="flex-1 overflow-y-auto">
        {!selected ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-400">
            <ShieldCheck size={48} className="mb-3 text-slate-200" />
            <p className="text-sm font-medium">Select a policy</p>
            <p className="text-xs mt-1">Click a GPO to see its links and details</p>
          </div>
        ) : (
          <GPODetail gpo={selected} detail={detail} loading={detailLoading} />
        )}
      </div>
    </div>
  )
}

// ── GPO detail panel ──────────────────────────────────────────────────────────

function GPODetail({ gpo, detail, loading }) {
  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      {/* Title */}
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
          <StatusIcon status={gpo.status} size={20} />
        </div>
        <div className="min-w-0">
          <h2 className="text-lg font-bold text-slate-900 leading-tight">{gpo.name}</h2>
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            <StatusBadge status={gpo.status} />
            <span className="text-xs text-slate-400">GUID: {gpo.guid}</span>
          </div>
        </div>
      </div>

      {/* Meta */}
      <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
        {gpo.description && (
          <div className="px-4 py-3">
            <p className="text-sm text-slate-600">{gpo.description}</p>
          </div>
        )}
        <div className="px-4 py-3 grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
          {gpo.when_created && (
            <MetaRow label="Created" value={gpo.when_created.split('T')[0]} />
          )}
          {gpo.when_changed && (
            <MetaRow label="Last Modified" value={gpo.when_changed.split('T')[0]} />
          )}
          {gpo.security_filters?.length > 0 && (
            <div className="col-span-2">
              <span className="text-xs text-slate-400 block mb-1">Security Filtering</span>
              <div className="flex flex-wrap gap-1">
                {gpo.security_filters.map((f) => (
                  <span key={f} className="bg-slate-100 text-slate-600 text-xs px-2 py-0.5 rounded-full">
                    {f}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Linked OUs */}
      <div>
        <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
          <Link size={12} />
          Linked Locations
        </h3>

        {loading ? (
          <div className="bg-white rounded-xl border border-slate-200 flex items-center justify-center h-24 text-slate-400">
            <Loader2 size={18} className="animate-spin" />
          </div>
        ) : detail?.error ? (
          <div className="bg-white rounded-xl border border-red-200 px-4 py-3 text-red-600 text-sm">
            {detail.error}
          </div>
        ) : detail?.linked_ous?.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 px-4 py-6 text-center text-slate-400 text-sm">
            This GPO is not linked to any location
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100 overflow-hidden">
            {detail?.linked_ous?.map((ou) => (
              <div key={ou.ou_dn} className="flex items-center gap-3 px-4 py-3">
                <Folder size={14} className="text-amber-500 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <span className="text-sm font-medium text-slate-800 block truncate">
                    {ou.ou_name}
                  </span>
                  <span className="text-xs text-slate-400 font-mono truncate block">
                    {ou.ou_dn}
                  </span>
                </div>
                <div className="flex items-center gap-1.5 flex-shrink-0">
                  {ou.enforced && (
                    <span className="bg-orange-100 text-orange-600 text-xs font-semibold px-2 py-0.5 rounded-full">
                      Enforced
                    </span>
                  )}
                  {!ou.link_enabled && (
                    <span className="bg-slate-100 text-slate-500 text-xs font-semibold px-2 py-0.5 rounded-full">
                      Disabled
                    </span>
                  )}
                  <span className="text-xs text-slate-300">#{ou.order}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function StatusIcon({ status, size = 14 }) {
  if (status === 'disabled')
    return <ShieldOff size={size} className="text-slate-400" />
  if (status === 'user_settings_disabled' || status === 'computer_settings_disabled')
    return <ShieldAlert size={size} className="text-amber-500" />
  return <ShieldCheck size={size} className="text-indigo-500" />
}

function StatusBadge({ status }) {
  const map = {
    enabled: 'bg-emerald-100 text-emerald-700',
    disabled: 'bg-slate-100 text-slate-500',
    user_settings_disabled: 'bg-amber-100 text-amber-700',
    computer_settings_disabled: 'bg-amber-100 text-amber-700',
  }
  const labels = {
    enabled: 'Enabled',
    disabled: 'Disabled',
    user_settings_disabled: 'User Settings Disabled',
    computer_settings_disabled: 'Computer Settings Disabled',
  }
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${map[status] || map.enabled}`}>
      {labels[status] || status}
    </span>
  )
}

function MetaRow({ label, value }) {
  return (
    <div>
      <span className="text-xs text-slate-400 block">{label}</span>
      <span className="text-sm text-slate-700">{value}</span>
    </div>
  )
}
