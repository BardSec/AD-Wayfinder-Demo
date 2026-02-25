import os
from dotenv import load_dotenv

load_dotenv()

def _read_secret(file_env_var, fallback_env_var, default=''):
    """Read a value from a Docker secret file, falling back to an env var."""
    file_path = os.getenv(file_env_var)
    if file_path:
        try:
            with open(file_path) as f:
                return f.read().strip()
        except OSError:
            pass
    return os.getenv(fallback_env_var, default)

AD_HOST = os.getenv('AD_HOST', 'localhost')
AD_PORT = int(os.getenv('AD_PORT', 389))
AD_USER = os.getenv('AD_USER', '')
AD_PASSWORD = _read_secret('AD_PASSWORD_FILE', 'AD_PASSWORD')
AD_BASE_DN = os.getenv('AD_BASE_DN', 'DC=acme,DC=local')
AD_USE_SSL = os.getenv('AD_USE_SSL', 'false').lower() == 'true'
AD_USE_TLS = os.getenv('AD_USE_TLS', 'false').lower() == 'true'

USE_MOCK_DATA = os.getenv('USE_MOCK_DATA', 'true').lower() == 'true'
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
STALE_ACCOUNT_DAYS = int(os.getenv('STALE_ACCOUNT_DAYS', 180))
