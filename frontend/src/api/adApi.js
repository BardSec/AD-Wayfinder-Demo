const BASE = '/api'

async function _get(path) {
  const res = await fetch(`${BASE}${path}`)
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
}
