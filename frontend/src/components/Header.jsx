import { useState, useRef, useEffect } from 'react'
import { Search, AlertTriangle, Network, X, User, Users, Folder } from 'lucide-react'

const TYPE_ICON = {
  user: <User size={14} className="text-slate-500" />,
  group: <Users size={14} className="text-green-600" />,
  ou: <Folder size={14} className="text-amber-600" />,
}

export default function Header({
  view, onViewChange, alertCount,
  onSearch, searchResults, onSearchSelect, onSearchClear,
}) {
  const [query, setQuery] = useState('')
  const inputRef = useRef(null)
  const debounceRef = useRef(null)

  const handleChange = (e) => {
    const val = e.target.value
    setQuery(val)
    clearTimeout(debounceRef.current)
    if (!val) { onSearchClear(); return }
    debounceRef.current = setTimeout(() => onSearch(val), 300)
  }

  const clear = () => {
    setQuery('')
    onSearchClear()
    inputRef.current?.focus()
  }

  // Close dropdown on Escape
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') clear() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  return (
    <header className="bg-slate-900 text-white px-4 py-0 flex items-center gap-4 shadow-lg z-20 flex-shrink-0" style={{ height: 56 }}>
      {/* Brand */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <Network size={22} className="text-indigo-400" />
        <span className="font-bold text-lg tracking-tight">AD Wayfinder</span>
      </div>

      {/* Nav tabs */}
      <nav className="flex items-center gap-1 ml-2">
        <TabBtn active={view === 'topology'} onClick={() => onViewChange('topology')}>
          Topology
        </TabBtn>
        <TabBtn active={view === 'alerts'} onClick={() => onViewChange('alerts')}>
          Alerts
          {alertCount > 0 && (
            <span className="ml-1.5 bg-red-500 text-white text-xs font-bold px-1.5 py-0.5 rounded-full leading-none">
              {alertCount}
            </span>
          )}
        </TabBtn>
      </nav>

      {/* Search */}
      <div className="relative flex-1 max-w-md ml-auto">
        <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleChange}
          placeholder="Search users, groups, OUs…"
          className="w-full bg-slate-800 text-slate-100 placeholder-slate-400 text-sm rounded-lg pl-9 pr-8 py-2 border border-slate-700 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        />
        {query && (
          <button onClick={clear} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200">
            <X size={14} />
          </button>
        )}

        {/* Dropdown */}
        {searchResults !== null && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-xl border border-slate-200 z-50 overflow-hidden">
            {searchResults.length === 0 ? (
              <p className="text-slate-500 text-sm px-4 py-3">No results found</p>
            ) : (
              <ul>
                {searchResults.map((r) => (
                  <li key={r.dn}>
                    <button
                      onClick={() => { onSearchSelect(r); setQuery('') }}
                      className="w-full flex items-center gap-2.5 px-4 py-2.5 text-left hover:bg-slate-50 text-sm"
                    >
                      <span className="flex-shrink-0">{TYPE_ICON[r.type]}</span>
                      <span className="flex-1 min-w-0">
                        <span className="font-medium text-slate-800 truncate block">
                          {r.name}
                          {r.sam && r.sam !== r.name && (
                            <span className="text-slate-400 font-normal ml-1">({r.sam})</span>
                          )}
                        </span>
                        {r.stale && (
                          <span className="text-xs text-red-600 flex items-center gap-1">
                            <AlertTriangle size={10} /> Stale account
                          </span>
                        )}
                      </span>
                      <span className="flex-shrink-0 text-xs text-slate-400 capitalize">{r.type}</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>

      {/* Alert badge shortcut */}
      {alertCount > 0 && (
        <button
          onClick={() => onViewChange('alerts')}
          className="flex items-center gap-1.5 bg-red-600 hover:bg-red-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg flex-shrink-0"
        >
          <AlertTriangle size={13} />
          {alertCount} alert{alertCount !== 1 ? 's' : ''}
        </button>
      )}
    </header>
  )
}

function TabBtn({ active, onClick, children }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
        active
          ? 'bg-slate-700 text-white'
          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
      }`}
    >
      {children}
    </button>
  )
}
