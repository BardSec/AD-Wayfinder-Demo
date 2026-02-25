"""
Simple in-memory TTL cache for AD query results.

All API responses are cached for DEFAULT_TTL seconds (1 hour by default).
The cache is invalidated via the POST /api/refresh endpoint so users can
force a fresh pull from AD on demand.
"""
import time
import threading

_store: dict = {}
_lock = threading.Lock()

DEFAULT_TTL = 3600  # 1 hour


def get_or_set(key: str, fn, ttl: int = DEFAULT_TTL):
    """
    Return the cached value for *key*.
    If the entry is missing or expired, call fn() to produce a fresh value,
    store it with the given TTL, and return it.
    """
    with _lock:
        entry = _store.get(key)
        if entry and time.time() < entry['expires']:
            return entry['data']

    # Compute outside the lock so a slow AD query doesn't block other reads
    data = fn()

    with _lock:
        _store[key] = {
            'data': data,
            'expires': time.time() + ttl,
            'updated_at': time.time(),
        }

    return data


def invalidate_all():
    """Clear every cached entry (forces re-query on the next request)."""
    with _lock:
        _store.clear()


def last_updated() -> float | None:
    """
    Return the Unix timestamp of the most recently updated cache entry,
    or None if the cache is empty.
    """
    with _lock:
        if not _store:
            return None
        return max(e['updated_at'] for e in _store.values())
