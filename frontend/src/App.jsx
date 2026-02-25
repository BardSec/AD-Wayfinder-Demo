import { useState, useCallback, useEffect, useRef } from 'react'
import Header from './components/Header'
import TopologyMap from './components/TopologyMap'
import DetailPanel from './components/DetailPanel'
import AlertsPanel from './components/AlertsPanel'
import NewTodayPanel from './components/NewTodayPanel'
import { api } from './api/adApi'

const AUTO_REFRESH_MS = 60 * 60 * 1000  // 1 hour

export default function App() {
  const [view, setView] = useState('topology')  // 'topology' | 'alerts' | 'new-today'
  const [selectedNode, setSelectedNode] = useState(null)
  const [detailData, setDetailData] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const [searchResults, setSearchResults] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(new Date())
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)   // increment → remounts TopologyMap
  const [newTodayCount, setNewTodayCount] = useState(0)

  // ── Initial load ────────────────────────────────────────────────────────────
  useEffect(() => {
    Promise.all([api.getStats(), api.getNewToday()])
      .then(([s, nt]) => {
        setStats(s)
        setNewTodayCount(nt.length)
        setLastUpdated(new Date())
      })
      .catch(console.error)
  }, [])

  // ── Hourly auto-refresh ─────────────────────────────────────────────────────
  useEffect(() => {
    const interval = setInterval(doRefresh, AUTO_REFRESH_MS)
    return () => clearInterval(interval)
  }, [])

  // ── Manual / auto refresh handler ──────────────────────────────────────────
  const doRefresh = useCallback(async () => {
    setIsRefreshing(true)
    try {
      await api.triggerRefresh()                    // tell backend to clear cache
      setRefreshKey((k) => k + 1)                  // remount topology graph
      const [s, nt] = await Promise.all([api.getStats(), api.getNewToday()])
      setStats(s)
      setNewTodayCount(nt.length)
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Refresh failed:', err)
    } finally {
      setIsRefreshing(false)
    }
  }, [])

  // ── Node detail loader ──────────────────────────────────────────────────────
  const loadDetail = useCallback(async (node) => {
    setSelectedNode(node)
    setDetailData(null)
    setDetailLoading(true)
    try {
      let data
      if (node.type === 'domain') {
        data = await api.getStats()
        data = { ...data, type: 'domain_stats' }
      } else if (node.type === 'ou') {
        data = await api.getOU(node.dn)
      } else if (node.type === 'group') {
        data = await api.getGroup(node.dn)
      } else if (node.type === 'user') {
        data = await api.getUser(node.dn)
      }
      setDetailData(data)
    } catch (err) {
      setDetailData({ error: err.message })
    } finally {
      setDetailLoading(false)
    }
  }, [])

  const handleSearchSelect = useCallback((result) => {
    setSearchResults(null)
    setView('topology')
    loadDetail(result)
  }, [loadDetail])

  const handleSearch = useCallback(async (q) => {
    if (!q || q.length < 2) { setSearchResults(null); return }
    const results = await api.search(q)
    setSearchResults(results)
  }, [])

  const alertCount = stats?.stale_accounts ?? 0

  return (
    <div className="h-screen flex flex-col bg-slate-50 overflow-hidden">
      <Header
        view={view}
        onViewChange={(v) => { setView(v); setSearchResults(null) }}
        alertCount={alertCount}
        newTodayCount={newTodayCount}
        onSearch={handleSearch}
        searchResults={searchResults}
        onSearchSelect={handleSearchSelect}
        onSearchClear={() => setSearchResults(null)}
        lastUpdated={lastUpdated}
        isRefreshing={isRefreshing}
        onRefresh={doRefresh}
      />

      <main className="flex-1 flex overflow-hidden">
        {view === 'topology' && (
          <>
            <div className="flex-1 relative">
              <TopologyMap
                key={refreshKey}
                onNodeSelect={loadDetail}
                selectedDn={selectedNode?.dn}
              />
            </div>
            <DetailPanel
              node={selectedNode}
              data={detailData}
              loading={detailLoading}
              onNavigate={loadDetail}
            />
          </>
        )}
        {view === 'alerts' && (
          <AlertsPanel
            onUserSelect={(user) => { setView('topology'); loadDetail(user) }}
          />
        )}
        {view === 'new-today' && (
          <NewTodayPanel
            onUserSelect={(user) => { setView('topology'); loadDetail(user) }}
          />
        )}
      </main>
    </div>
  )
}
