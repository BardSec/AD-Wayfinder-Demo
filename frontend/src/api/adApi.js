const BASE = '/api'

async function _get(path) {
  const res = await fetch(`${BASE}${path}`)
  if (res.status === 401) {
    window.location.href = '/auth/login'
    return
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.error || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  getTree: () => _get('/tree'),
  getOU: (dn) => _get(`/ou?dn=${encodeURIComponent(dn)}`),
  getGroup: (dn) => _get(`/group?dn=${encodeURIComponent(dn)}`),
  getUser: (dn) => _get(`/user?dn=${encodeURIComponent(dn)}`),
  getAlerts: () => _get('/alerts'),
  getStats: () => _get('/stats'),
  search: (q) => _get(`/search?q=${encodeURIComponent(q)}`),
  getNewToday: () => _get('/new-today'),
  getLastUpdated: () => _get('/last-updated'),
  triggerRefresh: () =>
    fetch(`${BASE}/refresh`, { method: 'POST' }).then((r) => r.json()),
  getGPOs: () => _get('/gpos'),
  getGPO: (guid) => _get(`/gpo?guid=${encodeURIComponent(guid)}`),
  getOUGPOs: (dn) => _get(`/ou-gpos?dn=${encodeURIComponent(dn)}`),
}
