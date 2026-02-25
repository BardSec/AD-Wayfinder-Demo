import { useState, useEffect } from 'react'
import { AlertTriangle, User, Users, Folder, Globe, Clock, Shield,
         Mail, Phone, Building2, Calendar, Key, Hash, Loader2,
         ChevronRight, CheckCircle2, XCircle, ShieldCheck,
         ShieldAlert, ShieldOff, Lock } from 'lucide-react'
import { api } from '../api/adApi'

export default function DetailPanel({ node, data, loading, onNavigate }) {
  if (!node) {
    return (
      <aside className="w-80 bg-white border-l border-slate-200 flex flex-col items-center justify-center text-slate-400 flex-shrink-0">
        <Folder size={40} className="mb-3 text-slate-300" />
        <p className="text-sm font-medium">Select a node</p>
        <p className="text-xs mt-1 text-center px-4">
          Click any domain, OU, or group in the graph to see details here
        </p>
      </aside>
    )
  }

  return (
    <aside className="w-96 bg-white border-l border-slate-200 flex flex-col flex-shrink-0 overflow-hidden detail-panel-enter">
      {/* Header */}
      <div className={`flex-shrink-0 px-4 py-3 border-b border-slate-100 ${nodeHeaderBg(node.type)}`}>
        <div className="flex items-center gap-2">
          <NodeIcon type={node.type} size={18} />
          <div className="min-w-0">
            <div className="font-bold text-sm text-slate-900 truncate">{node.name || node.display_name}</div>
            <div className="text-xs text-slate-500 capitalize">{node.type}</div>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center h-40 text-slate-400">
            <Loader2 size={24} className="animate-spin" />
          </div>
        ) : data?.error ? (
          <div className="p-4 text-red-600 text-sm">{data.error}</div>
        ) : data ? (
          <PanelBody data={data} onNavigate={onNavigate} />
        ) : null}
      </div>
    </aside>
  )
}

// ── Route to sub-view ─────────────────────────────────────────────────────────
function PanelBody({ data, onNavigate }) {
  if (data.type === 'domain_stats') return <DomainStats data={data} />
  if (data.type === 'ou') return <OUContents data={data} onNavigate={onNavigate} />
  if (data.type === 'group') return <GroupDetails data={data} onNavigate={onNavigate} />
  if (data.type === 'user') return <UserProfile data={data} onNavigate={onNavigate} />
  return null
}

// ── Domain stats ──────────────────────────────────────────────────────────────
function DomainStats({ data }) {
  return (
    <div className="p-4 space-y-3">
      <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Domain Summary</p>
      <div className="grid grid-cols-2 gap-2">
        <StatCard label="Total Users" value={data.total_users} color="text-indigo-600" />
        <StatCard label="Enabled" value={data.enabled_users} color="text-emerald-600" />
        <StatCard label="Disabled" value={data.disabled_users} color="text-slate-500" />
        <StatCard label="Stale Accounts" value={data.stale_accounts} color="text-red-600" />
        <StatCard label="Groups" value={data.total_groups} color="text-amber-600" />
        <StatCard label="OUs" value={data.total_ous} color="text-amber-600" />
      </div>
      {data.stale_threshold_days && (
        <p className="text-xs text-slate-400 mt-2">
          Stale = enabled but no login in {data.stale_threshold_days}+ days
        </p>
      )}
    </div>
  )
}

// ── OU contents ───────────────────────────────────────────────────────────────
function OUContents({ data, onNavigate }) {
  const [gpoData, setGpoData] = useState(null)
  const [gpoLoading, setGpoLoading] = useState(true)

  useEffect(() => {
    setGpoData(null)
    setGpoLoading(true)
    api.getOUGPOs(data.dn)
      .then(setGpoData)
      .catch(() => setGpoData({ direct: [], inherited: [], blocks_inheritance: false }))
      .finally(() => setGpoLoading(false))
  }, [data.dn])

  const allGpos = gpoData
    ? [...(gpoData.direct || []), ...(gpoData.inherited || [])]
    : []

  return (
    <div className="divide-y divide-slate-100">
      {/* Counts */}
      <div className="px-4 py-3 grid grid-cols-4 gap-2 text-center">
        <CountBadge value={data.counts?.ous} label="OUs" />
        <CountBadge value={data.counts?.groups} label="Groups" />
        <CountBadge value={data.counts?.users} label="Users" />
        <CountBadge value={data.counts?.computers} label="Computers" />
      </div>

      {data.description && (
        <div className="px-4 py-2 text-xs text-slate-500">{data.description}</div>
      )}

      {/* Child OUs */}
      {data.child_ous?.length > 0 && (
        <Section title="Child OUs" icon={<Folder size={13} className="text-amber-500" />}>
          {data.child_ous.map((ou) => (
            <ItemRow
              key={ou.dn}
              icon={<Folder size={14} className="text-amber-400" />}
              label={ou.name}
              sub={ou.description}
              onClick={() => onNavigate(ou)}
            />
          ))}
        </Section>
      )}

      {/* Groups */}
      {data.groups?.length > 0 && (
        <Section title="Groups" icon={<Users size={13} className="text-emerald-500" />}>
          {data.groups.map((g) => (
            <ItemRow
              key={g.dn}
              icon={<Users size={14} className="text-emerald-500" />}
              label={g.name}
              sub={`${g.member_count} member${g.member_count !== 1 ? 's' : ''}`}
              onClick={() => onNavigate(g)}
            />
          ))}
        </Section>
      )}

      {/* Users */}
      {data.users?.length > 0 && (
        <Section title="Users" icon={<User size={13} className="text-slate-500" />}>
          {data.users.map((u) => (
            <UserRow key={u.dn} user={u} onClick={() => onNavigate(u)} />
          ))}
        </Section>
      )}

      {data.child_ous?.length === 0 && data.groups?.length === 0 && data.users?.length === 0 && (
        <div className="px-4 py-6 text-slate-400 text-sm text-center">This OU is empty</div>
      )}

      {/* Group Policy */}
      <Section
        title="Group Policy"
        icon={<ShieldCheck size={13} className="text-indigo-500" />}
      >
        {gpoLoading ? (
          <div className="px-4 py-3 flex items-center gap-2 text-slate-400 text-sm">
            <Loader2 size={13} className="animate-spin" /> Loading policies…
          </div>
        ) : (
          <>
            {gpoData?.blocks_inheritance && (
              <div className="mx-4 my-2 flex items-center gap-1.5 bg-amber-50 border border-amber-200 rounded px-2.5 py-1.5 text-xs text-amber-700">
                <Lock size={11} className="flex-shrink-0" />
                Block Inheritance enabled — parent GPOs blocked (except enforced)
              </div>
            )}
            {allGpos.length === 0 && (
              <p className="px-4 py-2 text-slate-400 text-sm">No policies applied</p>
            )}
            {gpoData?.direct?.map((g) => (
              <GPOLinkRow key={g.guid} link={g} />
            ))}
            {gpoData?.inherited?.map((g) => (
              <GPOLinkRow key={`${g.guid}:${g.inherited_from_dn}`} link={g} />
            ))}
          </>
        )}
      </Section>
    </div>
  )
}

function GPOLinkRow({ link }) {
  const isInherited = link.source === 'inherited'
  const isDisabled = !link.link_enabled

  return (
    <div className="flex items-start gap-2.5 px-4 py-2.5 border-b border-slate-50 last:border-0">
      <span className="flex-shrink-0 mt-0.5">
        {isDisabled
          ? <ShieldOff size={13} className="text-slate-300" />
          : link.enforced
            ? <ShieldAlert size={13} className="text-orange-500" />
            : <ShieldCheck size={13} className="text-indigo-400" />
        }
      </span>
      <span className="flex-1 min-w-0">
        <span className={`text-sm truncate block ${isDisabled ? 'text-slate-400 line-through' : 'text-slate-800'}`}>
          {link.name}
        </span>
        <span className="text-xs text-slate-400 flex items-center gap-1.5 flex-wrap">
          {isInherited && (
            <span>from {link.inherited_from}</span>
          )}
          {link.enforced && (
            <span className="bg-orange-100 text-orange-600 px-1 rounded font-medium">Enforced</span>
          )}
          {isDisabled && (
            <span className="bg-slate-100 text-slate-500 px-1 rounded">Link disabled</span>
          )}
          {!isInherited && !link.enforced && !isDisabled && (
            <span className="text-slate-300">Order {link.order}</span>
          )}
        </span>
      </span>
    </div>
  )
}

// ── Group details ─────────────────────────────────────────────────────────────
function GroupDetails({ data, onNavigate }) {
  return (
    <div className="divide-y divide-slate-100">
      <div className="px-4 py-3 space-y-1">
        {data.description && <p className="text-sm text-slate-600">{data.description}</p>}
        <div className="flex flex-wrap gap-2 text-xs">
          <Badge label={data.group_type} color="bg-emerald-100 text-emerald-700" />
          {data.when_created && (
            <span className="text-slate-400">Created {data.when_created.split('T')[0]}</span>
          )}
        </div>
      </div>

      <Section title={`Members (${data.member_count})`} icon={<Users size={13} className="text-emerald-500" />}>
        {data.members?.length === 0 && (
          <p className="px-4 py-2 text-slate-400 text-sm">No members</p>
        )}
        {data.members?.map((m) =>
          m.type === 'user' ? (
            <UserRow key={m.dn} user={m} onClick={() => onNavigate(m)} />
          ) : (
            <ItemRow
              key={m.dn}
              icon={<Users size={14} className="text-emerald-500" />}
              label={m.name}
              sub={m.type === 'group' ? `Nested group · ${m.member_count ?? '?'} members` : m.type}
              onClick={() => onNavigate(m)}
            />
          )
        )}
      </Section>
    </div>
  )
}

// ── User profile ──────────────────────────────────────────────────────────────
function UserProfile({ data, onNavigate }) {
  return (
    <div className="divide-y divide-slate-100">
      {/* Alerts */}
      {data.alerts?.length > 0 && (
        <div className="px-4 py-3 space-y-2">
          {data.alerts.map((a, i) => (
            <div key={i} className="flex items-start gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              <AlertTriangle size={14} className="text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-xs text-red-700">{a.message}</p>
            </div>
          ))}
        </div>
      )}

      {/* Identity */}
      <div className="px-4 py-3 space-y-2">
        <Row icon={<User size={13} />} label="Display Name" value={data.display_name} />
        <Row icon={<Hash size={13} />} label="Username" value={data.sam} mono />
        <Row icon={<Mail size={13} />} label="Email" value={data.email} />
        <Row icon={<Phone size={13} />} label="Phone" value={data.phone} />
        <Row icon={<Building2 size={13} />} label="Department" value={data.department} />
        <Row icon={<Shield size={13} />} label="Title" value={data.title} />
        <Row icon={<Building2 size={13} />} label="Company" value={data.company} />
      </div>

      {/* Account status */}
      <div className="px-4 py-3 space-y-2">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Account Status</p>
        <div className="flex items-center gap-2">
          {data.enabled ? (
            <CheckCircle2 size={15} className="text-emerald-500" />
          ) : (
            <XCircle size={15} className="text-slate-400" />
          )}
          <span className={`text-sm font-medium ${data.enabled ? 'text-emerald-700' : 'text-slate-500'}`}>
            {data.enabled ? 'Enabled' : 'Disabled'}
          </span>
          {data.stale && (
            <span className="ml-1 bg-red-100 text-red-600 text-xs font-semibold px-2 py-0.5 rounded-full">
              Stale
            </span>
          )}
        </div>
        <Row icon={<Clock size={13} />} label="Last Login"
          value={data.last_logon ? fmtDate(data.last_logon) : 'Never'} />
        <Row icon={<Key size={13} />} label="Password Set"
          value={data.password_last_set ? fmtDate(data.password_last_set) : '—'} />
        <Row icon={<Calendar size={13} />} label="Account Created"
          value={data.when_created ? data.when_created.split('T')[0] : '—'} />
        <Row icon={<Hash size={13} />} label="Logon Count" value={data.logon_count ?? '—'} />
        <Row icon={<AlertTriangle size={13} />} label="Bad Password Count" value={data.bad_pwd_count ?? '—'} />
      </div>

      {/* Group memberships */}
      {data.member_of?.length > 0 && (
        <Section title="Group Memberships" icon={<Users size={13} className="text-emerald-500" />}>
          {data.member_of.map((g) => (
            <ItemRow
              key={g.dn || g}
              icon={<Users size={14} className="text-emerald-500" />}
              label={g.name || g}
              onClick={g.dn ? () => onNavigate({ type: 'group', dn: g.dn, name: g.name }) : undefined}
            />
          ))}
        </Section>
      )}

      {/* DN */}
      <div className="px-4 py-3">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">Distinguished Name</p>
        <p className="text-xs text-slate-500 font-mono break-all bg-slate-50 rounded px-2 py-1.5">{data.dn}</p>
      </div>
    </div>
  )
}

// ── Shared sub-components ─────────────────────────────────────────────────────

function Section({ title, icon, children }) {
  return (
    <div>
      <div className="flex items-center gap-1.5 px-4 py-2 bg-slate-50 border-b border-slate-100">
        {icon}
        <span className="text-xs font-semibold text-slate-600 uppercase tracking-wide">{title}</span>
      </div>
      <div className="divide-y divide-slate-50">{children}</div>
    </div>
  )
}

function ItemRow({ icon, label, sub, onClick }) {
  return (
    <button
      onClick={onClick}
      disabled={!onClick}
      className="w-full flex items-center gap-2.5 px-4 py-2.5 text-left hover:bg-slate-50 transition-colors disabled:cursor-default"
    >
      <span className="flex-shrink-0">{icon}</span>
      <span className="flex-1 min-w-0">
        <span className="text-sm text-slate-800 truncate block">{label}</span>
        {sub && <span className="text-xs text-slate-400 truncate block">{sub}</span>}
      </span>
      {onClick && <ChevronRight size={14} className="text-slate-300 flex-shrink-0" />}
    </button>
  )
}

function UserRow({ user, onClick }) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-2.5 px-4 py-2.5 text-left hover:bg-slate-50 transition-colors"
    >
      <div className="flex-shrink-0 w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center">
        <User size={13} className="text-slate-500" />
      </div>
      <span className="flex-1 min-w-0">
        <span className="text-sm text-slate-800 truncate flex items-center gap-1.5">
          {user.name}
          {!user.enabled && (
            <span className="text-xs text-slate-400 font-normal">(disabled)</span>
          )}
          {user.stale && user.enabled && (
            <AlertTriangle size={11} className="text-red-500 flex-shrink-0" />
          )}
        </span>
        {(user.title || user.sam) && (
          <span className="text-xs text-slate-400 truncate block">{user.title || user.sam}</span>
        )}
      </span>
      <ChevronRight size={14} className="text-slate-300 flex-shrink-0" />
    </button>
  )
}

function Row({ icon, label, value, mono }) {
  if (value == null || value === '') return null
  return (
    <div className="flex items-start gap-2">
      <span className="text-slate-400 flex-shrink-0 mt-0.5">{icon}</span>
      <div className="min-w-0">
        <span className="text-xs text-slate-400">{label}</span>
        <p className={`text-sm text-slate-800 truncate ${mono ? 'font-mono' : ''}`}>{String(value)}</p>
      </div>
    </div>
  )
}

function Badge({ label, color }) {
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>{label}</span>
}

function StatCard({ label, value, color }) {
  return (
    <div className="bg-slate-50 rounded-lg p-2 text-center">
      <div className={`text-xl font-bold ${color}`}>{value ?? '—'}</div>
      <div className="text-xs text-slate-500">{label}</div>
    </div>
  )
}

function CountBadge({ value, label }) {
  return (
    <div className="text-center">
      <div className="text-lg font-bold text-slate-700">{value ?? 0}</div>
      <div className="text-xs text-slate-400">{label}</div>
    </div>
  )
}

function nodeHeaderBg(type) {
  if (type === 'domain') return 'bg-indigo-50 border-indigo-100'
  if (type === 'ou') return 'bg-amber-50 border-amber-100'
  if (type === 'group') return 'bg-emerald-50 border-emerald-100'
  if (type === 'user') return 'bg-slate-50 border-slate-100'
  return 'bg-slate-50'
}

function NodeIcon({ type, size }) {
  if (type === 'domain') return <Globe size={size} className="text-indigo-500 flex-shrink-0" />
  if (type === 'ou') return <Folder size={size} className="text-amber-500 flex-shrink-0" />
  if (type === 'group') return <Users size={size} className="text-emerald-500 flex-shrink-0" />
  return <User size={size} className="text-slate-500 flex-shrink-0" />
}

function fmtDate(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}
