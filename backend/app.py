"""
AD Wayfinder — Flask API
"""
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import config as cfg
import cache as _cache

app = Flask(__name__)
CORS(app)


def _get_client():
    if cfg.USE_MOCK_DATA:
        from mock_data import MockADClient
        return MockADClient()
    from ad_client import ADClient
    return ADClient()


def _err(msg, status=400):
    return jsonify({'error': msg}), status


# ─── Core tree / detail endpoints (1-hour cache) ──────────────────────────────

@app.route('/api/tree')
def tree():
    try:
        return jsonify(_cache.get_or_set('tree', lambda: _get_client().get_tree()))
    except Exception as e:
        return _err(str(e), 500)


@app.route('/api/ou')
def ou():
    dn = request.args.get('dn', '').strip()
    if not dn:
        return _err('dn parameter is required')
    try:
        data = _cache.get_or_set(f'ou:{dn}', lambda: _get_client().get_ou_contents(dn))
        if data is None:
            return _err('OU not found', 404)
        return jsonify(data)
    except Exception as e:
        return _err(str(e), 500)


@app.route('/api/group')
def group():
    dn = request.args.get('dn', '').strip()
    if not dn:
        return _err('dn parameter is required')
    try:
        data = _cache.get_or_set(f'group:{dn}', lambda: _get_client().get_group_details(dn))
        if data is None:
            return _err('Group not found', 404)
        return jsonify(data)
    except Exception as e:
        return _err(str(e), 500)


@app.route('/api/user')
def user():
    dn = request.args.get('dn', '').strip()
    if not dn:
        return _err('dn parameter is required')
    try:
        data = _cache.get_or_set(f'user:{dn}', lambda: _get_client().get_user_details(dn))
        if data is None:
            return _err('User not found', 404)
        return jsonify(data)
    except Exception as e:
        return _err(str(e), 500)


@app.route('/api/alerts')
def alerts():
    try:
        return jsonify(_cache.get_or_set('alerts', lambda: _get_client().get_alerts()))
    except Exception as e:
        return _err(str(e), 500)


@app.route('/api/stats')
def stats():
    try:
        return jsonify(_cache.get_or_set('stats', lambda: _get_client().get_stats()))
    except Exception as e:
        return _err(str(e), 500)


# ─── New-today onboarding endpoint (15-min cache) ────────────────────────────

@app.route('/api/new-today')
def new_today():
    """
    Return all user accounts whose whenCreated falls within the current
    calendar day.  Shorter TTL (15 min) so new hires appear promptly.
    """
    try:
        return jsonify(_cache.get_or_set(
            'new_today',
            lambda: _get_client().get_new_today(),
            ttl=900,
        ))
    except Exception as e:
        return _err(str(e), 500)


# ─── Search (never cached — always live) ─────────────────────────────────────

@app.route('/api/search')
def search():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    try:
        return jsonify(_get_client().search(q))
    except Exception as e:
        return _err(str(e), 500)


# ─── Cache management ─────────────────────────────────────────────────────────

@app.route('/api/last-updated')
def last_updated():
    """Return ISO timestamp of the most recent cache population."""
    ts = _cache.last_updated()
    return jsonify({
        'timestamp': ts,
        'iso': datetime.fromtimestamp(ts).isoformat() if ts else None,
    })


@app.route('/api/refresh', methods=['POST'])
def refresh():
    """Invalidate all cached entries — next request re-queries AD."""
    _cache.invalidate_all()
    return jsonify({'status': 'ok', 'message': 'Cache cleared'})


# ─── Health ───────────────────────────────────────────────────────────────────

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'mock_mode': cfg.USE_MOCK_DATA,
        'stale_threshold_days': cfg.STALE_ACCOUNT_DAYS,
    })


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    mode = 'DEMO (mock data)' if cfg.USE_MOCK_DATA else f'LIVE ({cfg.AD_HOST})'
    print(f'AD Wayfinder backend starting — {mode}')
    app.run(host='0.0.0.0', port=cfg.FLASK_PORT, debug=(cfg.FLASK_PORT == 5000))
