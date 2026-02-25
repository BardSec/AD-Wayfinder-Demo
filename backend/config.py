import os
from dotenv import load_dotenv

load_dotenv()

AD_HOST = os.getenv('AD_HOST', 'localhost')
AD_PORT = int(os.getenv('AD_PORT', 389))
AD_USER = os.getenv('AD_USER', '')
AD_PASSWORD = os.getenv('AD_PASSWORD', '')
AD_BASE_DN = os.getenv('AD_BASE_DN', 'DC=acme,DC=local')
AD_USE_SSL = os.getenv('AD_USE_SSL', 'false').lower() == 'true'
AD_USE_TLS = os.getenv('AD_USE_TLS', 'false').lower() == 'true'

USE_MOCK_DATA = os.getenv('USE_MOCK_DATA', 'true').lower() == 'true'
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
STALE_ACCOUNT_DAYS = int(os.getenv('STALE_ACCOUNT_DAYS', 180))
