"""
Microsoft Entra ID (Azure AD) authentication via MSAL.
Blueprint providing: /auth/login  /auth/callback  /auth/logout  /auth/me

Flow:
  1. Browser → GET /auth/login  → redirect to Microsoft login
  2. Microsoft → GET /auth/callback?code=…  → exchange code, check group, set session
  3. All /api/* routes check session via require_auth decorator
  4. Browser → GET /auth/logout → clear session, redirect to Microsoft logout
"""
import requests
from functools import wraps
from flask import Blueprint, redirect, request, session, jsonify
import msal
import config as cfg

auth_bp = Blueprint('auth', __name__)

_AUTHORITY = f'https://login.microsoftonline.com/{cfg.AZURE_TENANT_ID}'
_GRAPH = 'https://graph.microsoft.com/v1.0'


def _scopes():
    """Only request GroupMember.Read.All when group restriction is configured."""
    scopes = ['User.Read']
    if cfg.ALLOWED_GROUP_ID:
        scopes.append('GroupMember.Read.All')
    return scopes


def _msal_app():
    return msal.ConfidentialClientApplication(
        cfg.AZURE_CLIENT_ID,
        authority=_AUTHORITY,
        client_credential=cfg.AZURE_CLIENT_SECRET,
    )


def _in_allowed_group(access_token):
    """Return True if the signed-in user is a member of ALLOWED_GROUP_ID."""
    if not cfg.ALLOWED_GROUP_ID:
        return True
    resp = requests.post(
        f'{_GRAPH}/me/checkMemberOf',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'groupIds': [cfg.ALLOWED_GROUP_ID]},
        timeout=10,
    )
    return cfg.ALLOWED_GROUP_ID in resp.json().get('value', []) if resp.ok else False


def require_auth(f):
    """Decorator — returns 401 JSON if AUTH_ENABLED and no valid session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not cfg.AUTH_ENABLED:
            return f(*args, **kwargs)
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


# ─── Routes ──────────────────────────────────────────────────────────────────

@auth_bp.route('/auth/login')
def login():
    flow = _msal_app().initiate_auth_code_flow(
        scopes=_scopes(),
        redirect_uri=cfg.AZURE_REDIRECT_URI,
    )
    session['flow'] = flow
    return redirect(flow['auth_uri'])


@auth_bp.route('/auth/callback')
def callback():
    result = _msal_app().acquire_token_by_auth_code_flow(
        session.pop('flow', {}),
        request.args,
    )
    if 'error' in result:
        return jsonify({'error': result.get('error_description', 'Authentication failed')}), 401

    if not _in_allowed_group(result['access_token']):
        return (
            jsonify({'error': 'Access denied: your account is not in the required group'}),
            403,
        )

    claims = result.get('id_token_claims', {})
    session['user'] = {
        'name': claims.get('name', ''),
        'email': claims.get('preferred_username', ''),
        'oid': claims.get('oid', ''),
    }
    return redirect('/')


@auth_bp.route('/auth/logout')
def logout():
    session.clear()
    return redirect(
        f'{_AUTHORITY}/oauth2/v2.0/logout'
        f'?post_logout_redirect_uri={cfg.AZURE_POST_LOGOUT_URI}'
    )


@auth_bp.route('/auth/me')
def me():
    if 'user' not in session:
        return jsonify({'authenticated': False}), 401
    return jsonify({'authenticated': True, 'user': session['user']})
