import { useState, useCallback, useEffect } from 'react'
import Header from './components/Header'
import TopologyMap from './components/TopologyMap'
import DetailPanel from './components/DetailPanel'
import AlertsPanel from './components/AlertsPanel'
import { api } from './api/adApi'

export default function App() {
  const [view, setView] = useState('topology')        // 'topology' | 'alerts'
  const [selectedNode, setSelectedNode] = useState(null)
  const [detailData, setDetailData] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const [searchResults, setSearchResults] = useState(null)

  // Load summary stats on mount (drives alert badge in header)
  useEffect(() => {
    api.getStats().then(setStats).catch(console.error)
  }, [])

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

  // When a search result is clicked, switch to topology view and show detail
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
        onSearch={handleSearch}
        searchResults={searchResults}
        onSearchSelect={handleSearchSelect}
        onSearchClear={() => setSearchResults(null)}
      />

      <main className="flex-1 flex overflow-hidden">
        {view === 'topology' ? (
          <>
            <div className="flex-1 relative">
              <TopologyMap
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
        ) : (
          <AlertsPanel
            onUserSelect={(user) => { setView('topology'); loadDetail(user) }}
          />
        )}
      </main>
    </div>
  )
}
