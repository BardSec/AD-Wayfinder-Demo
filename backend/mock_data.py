"""
Mock AD client — returns realistic sample data so the app can be evaluated
without a live Active Directory connection.  Toggle via USE_MOCK_DATA=true.
"""
from datetime import datetime, timedelta
import config as cfg


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _days_ago(n):
    """Return an ISO timestamp n days in the past (None if n is None)."""
    if n is None:
        return None
    return (datetime.now() - timedelta(days=n)).isoformat()


def _get_parent_dn(dn):
    """Strip the first RDN component to obtain the parent DN."""
    parts = dn.split(',', 1)
    return parts[1] if len(parts) > 1 else None


def _is_stale(last_logon_iso):
    if last_logon_iso is None:
        return True
    last = datetime.fromisoformat(last_logon_iso)
    return (datetime.now() - last).days > cfg.STALE_ACCOUNT_DAYS


def _is_enabled(uac):
    return not (int(uac) & 0x0002)


def _today():
    """Return today's ISO date string (YYYY-MM-DD)."""
    return datetime.now().date().isoformat()


# ─── Sample Data ─────────────────────────────────────────────────────────────

_OUS = {
    'DC=acme,DC=local': {
        'dn': 'DC=acme,DC=local', 'name': 'acme.local',
        'type': 'domain', 'description': 'Acme Corporation root domain',
    },
    'OU=Corporate,DC=acme,DC=local': {
        'dn': 'OU=Corporate,DC=acme,DC=local', 'name': 'Corporate',
        'type': 'ou', 'description': 'Corporate leadership & administration',
    },
    'OU=Executives,OU=Corporate,DC=acme,DC=local': {
        'dn': 'OU=Executives,OU=Corporate,DC=acme,DC=local', 'name': 'Executives',
        'type': 'ou', 'description': 'C-suite and VP-level accounts',
    },
    'OU=IT,DC=acme,DC=local': {
        'dn': 'OU=IT,DC=acme,DC=local', 'name': 'IT',
        'type': 'ou', 'description': 'Information Technology department',
    },
    'OU=Systems_Administration,OU=IT,DC=acme,DC=local': {
        'dn': 'OU=Systems_Administration,OU=IT,DC=acme,DC=local',
        'name': 'Systems Administration',
        'type': 'ou', 'description': 'Server and infrastructure admins',
    },
    'OU=Helpdesk,OU=IT,DC=acme,DC=local': {
        'dn': 'OU=Helpdesk,OU=IT,DC=acme,DC=local', 'name': 'Helpdesk',
        'type': 'ou', 'description': 'Level-1 and Level-2 support staff',
    },
    'OU=Finance,DC=acme,DC=local': {
        'dn': 'OU=Finance,DC=acme,DC=local', 'name': 'Finance',
        'type': 'ou', 'description': 'Finance and accounting team',
    },
    'OU=HR,DC=acme,DC=local': {
        'dn': 'OU=HR,DC=acme,DC=local', 'name': 'Human Resources',
        'type': 'ou', 'description': 'Human resources and people operations',
    },
    'OU=Operations,DC=acme,DC=local': {
        'dn': 'OU=Operations,DC=acme,DC=local', 'name': 'Operations',
        'type': 'ou', 'description': 'Warehouse and logistics operations',
    },
    'OU=Warehouse,OU=Operations,DC=acme,DC=local': {
        'dn': 'OU=Warehouse,OU=Operations,DC=acme,DC=local', 'name': 'Warehouse',
        'type': 'ou', 'description': 'Warehouse floor staff',
    },
    'OU=Logistics,OU=Operations,DC=acme,DC=local': {
        'dn': 'OU=Logistics,OU=Operations,DC=acme,DC=local', 'name': 'Logistics',
        'type': 'ou', 'description': 'Freight and supply-chain staff',
    },
    'OU=Service_Accounts,DC=acme,DC=local': {
        'dn': 'OU=Service_Accounts,DC=acme,DC=local', 'name': 'Service Accounts',
        'type': 'ou', 'description': 'Non-interactive service accounts',
    },
}

_USERS_RAW = [
    # ── Executives ────────────────────────────────────────────────────────────
    dict(dn='CN=Alice Johnson,OU=Executives,OU=Corporate,DC=acme,DC=local',
         sam='alice.johnson', display_name='Alice Johnson',
         first_name='Alice', last_name='Johnson',
         email='alice.johnson@acme.local', phone='+1 555-0101',
         department='Executive', title='Chief Executive Officer',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(5), when_created='2018-03-15',
         logon_count=1892, bad_pwd_count=0,
         member_of=['CN=GG_Corporate_All,OU=Corporate,DC=acme,DC=local']),

    dict(dn='CN=Bob Williams,OU=Executives,OU=Corporate,DC=acme,DC=local',
         sam='bob.williams', display_name='Bob Williams',
         first_name='Bob', last_name='Williams',
         email='bob.williams@acme.local', phone='+1 555-0102',
         department='Executive', title='Chief Financial Officer',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(72), when_created='2018-03-15',
         logon_count=1451, bad_pwd_count=0,
         member_of=['CN=GG_Corporate_All,OU=Corporate,DC=acme,DC=local']),

    dict(dn='CN=Carol Davis,OU=Executives,OU=Corporate,DC=acme,DC=local',
         sam='carol.davis', display_name='Carol Davis',
         first_name='Carol', last_name='Davis',
         email='carol.davis@acme.local', phone='+1 555-0103',
         department='Executive', title='Chief Technology Officer',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(46), when_created='2019-06-01',
         logon_count=987, bad_pwd_count=0,
         member_of=['CN=GG_Corporate_All,OU=Corporate,DC=acme,DC=local',
                    'CN=GG_IT_All,OU=IT,DC=acme,DC=local']),

    # ── IT / Systems Administration ───────────────────────────────────────────
    dict(dn='CN=Dave Anderson,OU=Systems_Administration,OU=IT,DC=acme,DC=local',
         sam='dave.anderson', display_name='Dave Anderson',
         first_name='Dave', last_name='Anderson',
         email='dave.anderson@acme.local', phone='+1 555-0201',
         department='IT', title='Senior Systems Administrator',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(1), when_created='2019-02-11',
         logon_count=3412, bad_pwd_count=0,
         member_of=['CN=GG_IT_Sysadmins,OU=Systems_Administration,OU=IT,DC=acme,DC=local',
                    'CN=GG_IT_All,OU=IT,DC=acme,DC=local',
                    'CN=GG_Domain_Admins,OU=IT,DC=acme,DC=local']),

    dict(dn='CN=Eve Martinez,OU=Systems_Administration,OU=IT,DC=acme,DC=local',
         sam='eve.martinez', display_name='Eve Martinez',
         first_name='Eve', last_name='Martinez',
         email='eve.martinez@acme.local', phone='+1 555-0202',
         department='IT', title='Systems Administrator',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(3), when_created='2020-08-17',
         logon_count=2100, bad_pwd_count=0,
         member_of=['CN=GG_IT_Sysadmins,OU=Systems_Administration,OU=IT,DC=acme,DC=local',
                    'CN=GG_IT_All,OU=IT,DC=acme,DC=local']),

    # ── IT / Helpdesk ─────────────────────────────────────────────────────────
    dict(dn='CN=Frank Thompson,OU=Helpdesk,OU=IT,DC=acme,DC=local',
         sam='frank.thompson', display_name='Frank Thompson',
         first_name='Frank', last_name='Thompson',
         email='frank.thompson@acme.local', phone='+1 555-0203',
         department='IT', title='Helpdesk Technician',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(116), when_created='2021-03-22',
         logon_count=744, bad_pwd_count=2,
         member_of=['CN=GG_IT_Helpdesk,OU=Helpdesk,OU=IT,DC=acme,DC=local',
                    'CN=GG_IT_All,OU=IT,DC=acme,DC=local']),

    # ── IT (OU root) ─────────────────────────────────────────────────────────
    dict(dn='CN=Grace Wilson,OU=IT,DC=acme,DC=local',
         sam='grace.wilson', display_name='Grace Wilson',
         first_name='Grace', last_name='Wilson',
         email='grace.wilson@acme.local', phone='+1 555-0200',
         department='IT', title='IT Manager',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(7), when_created='2018-06-05',
         logon_count=2891, bad_pwd_count=0,
         member_of=['CN=GG_IT_All,OU=IT,DC=acme,DC=local',
                    'CN=GG_Domain_Admins,OU=IT,DC=acme,DC=local']),

    # ── Finance ──────────────────────────────────────────────────────────────
    dict(dn='CN=Henry Brown,OU=Finance,DC=acme,DC=local',
         sam='henry.brown', display_name='Henry Brown',
         first_name='Henry', last_name='Brown',
         email='henry.brown@acme.local', phone='+1 555-0301',
         department='Finance', title='Finance Director',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(198),   # STALE — 198 days
         when_created='2017-11-20',
         logon_count=1654, bad_pwd_count=0,
         member_of=['CN=GG_Finance_All,OU=Finance,DC=acme,DC=local']),

    dict(dn='CN=Iris Garcia,OU=Finance,DC=acme,DC=local',
         sam='iris.garcia', display_name='Iris Garcia',
         first_name='Iris', last_name='Garcia',
         email='iris.garcia@acme.local', phone='+1 555-0302',
         department='Finance', title='Senior Accountant',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(51), when_created='2020-04-13',
         logon_count=1123, bad_pwd_count=0,
         member_of=['CN=GG_Finance_All,OU=Finance,DC=acme,DC=local']),

    dict(dn='CN=Jack Miller,OU=Finance,DC=acme,DC=local',
         sam='jack.miller', display_name='Jack Miller',
         first_name='Jack', last_name='Miller',
         email='jack.miller@acme.local', phone='+1 555-0303',
         department='Finance', title='Financial Analyst',
         company='Acme Corporation', uac=514,   # DISABLED (0x0002)
         last_logon=_days_ago(140), when_created='2021-09-08',
         logon_count=312, bad_pwd_count=0,
         member_of=['CN=GG_Finance_All,OU=Finance,DC=acme,DC=local']),

    dict(dn='CN=Karen Jones,OU=Finance,DC=acme,DC=local',
         sam='karen.jones', display_name='Karen Jones',
         first_name='Karen', last_name='Jones',
         email='karen.jones@acme.local', phone='+1 555-0304',
         department='Finance', title='Accountant',
         company='Acme Corporation', uac=512,
         last_logon=None,             # STALE — never logged in, account enabled
         when_created='2024-11-01',
         logon_count=0, bad_pwd_count=0,
         member_of=['CN=GG_Finance_All,OU=Finance,DC=acme,DC=local']),

    # ── Human Resources ──────────────────────────────────────────────────────
    dict(dn='CN=Larry Wilson,OU=HR,DC=acme,DC=local',
         sam='larry.wilson', display_name='Larry Wilson',
         first_name='Larry', last_name='Wilson',
         email='larry.wilson@acme.local', phone='+1 555-0401',
         department='Human Resources', title='HR Director',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(15), when_created='2018-09-10',
         logon_count=2034, bad_pwd_count=0,
         member_of=['CN=GG_HR_All,OU=HR,DC=acme,DC=local']),

    dict(dn='CN=Mary Taylor,OU=HR,DC=acme,DC=local',
         sam='mary.taylor', display_name='Mary Taylor',
         first_name='Mary', last_name='Taylor',
         email='mary.taylor@acme.local', phone='+1 555-0402',
         department='Human Resources', title='HR Specialist',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(452),   # STALE — over a year
         when_created='2019-12-02',
         logon_count=876, bad_pwd_count=0,
         member_of=['CN=GG_HR_All,OU=HR,DC=acme,DC=local']),

    # ── Operations / Warehouse ────────────────────────────────────────────────
    dict(dn='CN=Nathan Moore,OU=Warehouse,OU=Operations,DC=acme,DC=local',
         sam='nathan.moore', display_name='Nathan Moore',
         first_name='Nathan', last_name='Moore',
         email='nathan.moore@acme.local', phone='+1 555-0501',
         department='Operations', title='Warehouse Manager',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(225),   # STALE
         when_created='2019-05-14',
         logon_count=678, bad_pwd_count=1,
         member_of=['CN=GG_Operations_All,OU=Operations,DC=acme,DC=local']),

    dict(dn='CN=Olivia Jackson,OU=Warehouse,OU=Operations,DC=acme,DC=local',
         sam='olivia.jackson', display_name='Olivia Jackson',
         first_name='Olivia', last_name='Jackson',
         email='olivia.jackson@acme.local', phone='+1 555-0502',
         department='Operations', title='Warehouse Associate',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(24), when_created='2022-01-10',
         logon_count=445, bad_pwd_count=0,
         member_of=['CN=GG_Operations_All,OU=Operations,DC=acme,DC=local']),

    # ── Operations / Logistics ────────────────────────────────────────────────
    dict(dn='CN=Patrick Harris,OU=Logistics,OU=Operations,DC=acme,DC=local',
         sam='patrick.harris', display_name='Patrick Harris',
         first_name='Patrick', last_name='Harris',
         email='patrick.harris@acme.local', phone='+1 555-0503',
         department='Operations', title='Logistics Coordinator',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(158),   # 158 days — NOT stale (< 180)
         when_created='2020-07-22',
         logon_count=912, bad_pwd_count=0,
         member_of=['CN=GG_Operations_All,OU=Operations,DC=acme,DC=local']),

    dict(dn='CN=Quinn Martin,OU=Logistics,OU=Operations,DC=acme,DC=local',
         sam='quinn.martin', display_name='Quinn Martin',
         first_name='Quinn', last_name='Martin',
         email='quinn.martin@acme.local', phone='+1 555-0504',
         department='Operations', title='Logistics Analyst',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(11), when_created='2022-03-07',
         logon_count=567, bad_pwd_count=0,
         member_of=['CN=GG_Operations_All,OU=Operations,DC=acme,DC=local']),

    # ── Service Accounts ─────────────────────────────────────────────────────
    dict(dn='CN=svc_backup,OU=Service_Accounts,DC=acme,DC=local',
         sam='svc_backup', display_name='svc_backup',
         first_name=None, last_name=None,
         email=None, phone=None,
         department='IT', title='Service Account — Backup',
         company='Acme Corporation', uac=512,
         last_logon=None,             # STALE — never logged in
         when_created='2019-01-01',
         logon_count=0, bad_pwd_count=0,
         member_of=[]),

    dict(dn='CN=svc_monitoring,OU=Service_Accounts,DC=acme,DC=local',
         sam='svc_monitoring', display_name='svc_monitoring',
         first_name=None, last_name=None,
         email=None, phone=None,
         department='IT', title='Service Account — Monitoring',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(1), when_created='2020-05-12',
         logon_count=8934, bad_pwd_count=0,
         member_of=[]),

    dict(dn='CN=svc_oldapp,OU=Service_Accounts,DC=acme,DC=local',
         sam='svc_oldapp', display_name='svc_oldapp',
         first_name=None, last_name=None,
         email=None, phone=None,
         department='IT', title='Service Account — Legacy Application',
         company='Acme Corporation', uac=512,
         last_logon=_days_ago(972),   # STALE — nearly 3 years
         when_created='2017-03-15',
         logon_count=2341, bad_pwd_count=0,
         member_of=[]),

    # ── New hires (created today — for onboarding panel demo) ─────────────────
    dict(dn='CN=Tom Bradley,OU=Systems_Administration,OU=IT,DC=acme,DC=local',
         sam='tom.bradley', display_name='Tom Bradley',
         first_name='Tom', last_name='Bradley',
         email='tom.bradley@acme.local', phone='+1 555-0211',
         department='IT', title='Junior Systems Administrator',
         company='Acme Corporation', uac=512,
         last_logon=None,             # new hire — never logged in
         when_created=_today(),
         logon_count=0, bad_pwd_count=0,
         member_of=[]),               # no groups yet

    dict(dn='CN=Sophie Chen,OU=Finance,DC=acme,DC=local',
         sam='sophie.chen', display_name='Sophie Chen',
         first_name='Sophie', last_name='Chen',
         email='sophie.chen@acme.local', phone='+1 555-0311',
         department='Finance', title='Financial Analyst',
         company='Acme Corporation', uac=512,
         last_logon=None,             # new hire — never logged in
         when_created=_today(),
         logon_count=0, bad_pwd_count=0,
         member_of=['CN=GG_Finance_All,OU=Finance,DC=acme,DC=local']),

    dict(dn='CN=Marcus Lee,OU=Logistics,OU=Operations,DC=acme,DC=local',
         sam='marcus.lee', display_name='Marcus Lee',
         first_name='Marcus', last_name='Lee',
         email=None,                  # email not yet provisioned
         phone='+1 555-0511',
         department='Operations', title='Logistics Coordinator',
         company='Acme Corporation', uac=512,
         last_logon=None,             # new hire — never logged in
         when_created=_today(),
         logon_count=0, bad_pwd_count=0,
         member_of=[]),               # no groups yet
]

# Index by DN for fast lookup
_USERS = {u['dn']: u for u in _USERS_RAW}

_GROUPS = {
    'CN=GG_Corporate_All,OU=Corporate,DC=acme,DC=local': {
        'dn': 'CN=GG_Corporate_All,OU=Corporate,DC=acme,DC=local',
        'name': 'GG_Corporate_All', 'type': 'group',
        'description': 'All Corporate division staff',
        'group_type': 'Security Global',
        'when_created': '2018-01-15',
        'members': [
            'CN=Alice Johnson,OU=Executives,OU=Corporate,DC=acme,DC=local',
            'CN=Bob Williams,OU=Executives,OU=Corporate,DC=acme,DC=local',
            'CN=Carol Davis,OU=Executives,OU=Corporate,DC=acme,DC=local',
        ],
    },
    'CN=GG_IT_All,OU=IT,DC=acme,DC=local': {
        'dn': 'CN=GG_IT_All,OU=IT,DC=acme,DC=local',
        'name': 'GG_IT_All', 'type': 'group',
        'description': 'All IT department staff',
        'group_type': 'Security Global',
        'when_created': '2018-01-15',
        'members': [
            'CN=Dave Anderson,OU=Systems_Administration,OU=IT,DC=acme,DC=local',
            'CN=Eve Martinez,OU=Systems_Administration,OU=IT,DC=acme,DC=local',
            'CN=Frank Thompson,OU=Helpdesk,OU=IT,DC=acme,DC=local',
            'CN=Grace Wilson,OU=IT,DC=acme,DC=local',
            'CN=Carol Davis,OU=Executives,OU=Corporate,DC=acme,DC=local',
        ],
    },
    'CN=GG_IT_Sysadmins,OU=Systems_Administration,OU=IT,DC=acme,DC=local': {
        'dn': 'CN=GG_IT_Sysadmins,OU=Systems_Administration,OU=IT,DC=acme,DC=local',
        'name': 'GG_IT_Sysadmins', 'type': 'group',
        'description': 'Systems Administrators with elevated server access',
        'group_type': 'Security Global',
        'when_created': '2018-01-15',
        'members': [
            'CN=Dave Anderson,OU=Systems_Administration,OU=IT,DC=acme,DC=local',
            'CN=Eve Martinez,OU=Systems_Administration,OU=IT,DC=acme,DC=local',
        ],
    },
    'CN=GG_IT_Helpdesk,OU=Helpdesk,OU=IT,DC=acme,DC=local': {
        'dn': 'CN=GG_IT_Helpdesk,OU=Helpdesk,OU=IT,DC=acme,DC=local',
        'name': 'GG_IT_Helpdesk', 'type': 'group',
        'description': 'Level-1 and Level-2 support technicians',
        'group_type': 'Security Global',
        'when_created': '2019-03-01',
        'members': [
            'CN=Frank Thompson,OU=Helpdesk,OU=IT,DC=acme,DC=local',
        ],
    },
    'CN=GG_Domain_Admins,OU=IT,DC=acme,DC=local': {
        'dn': 'CN=GG_Domain_Admins,OU=IT,DC=acme,DC=local',
        'name': 'GG_Domain_Admins', 'type': 'group',
        'description': 'Domain administrators — highest privilege group',
        'group_type': 'Security Global',
        'when_created': '2017-01-01',
        'members': [
            'CN=Dave Anderson,OU=Systems_Administration,OU=IT,DC=acme,DC=local',
            'CN=Grace Wilson,OU=IT,DC=acme,DC=local',
            'CN=GG_IT_Sysadmins,OU=Systems_Administration,OU=IT,DC=acme,DC=local',
        ],
    },
    'CN=GG_Finance_All,OU=Finance,DC=acme,DC=local': {
        'dn': 'CN=GG_Finance_All,OU=Finance,DC=acme,DC=local',
        'name': 'GG_Finance_All', 'type': 'group',
        'description': 'All Finance and Accounting department staff',
        'group_type': 'Security Global',
        'when_created': '2018-01-15',
        'members': [
            'CN=Henry Brown,OU=Finance,DC=acme,DC=local',
            'CN=Iris Garcia,OU=Finance,DC=acme,DC=local',
            'CN=Jack Miller,OU=Finance,DC=acme,DC=local',
            'CN=Karen Jones,OU=Finance,DC=acme,DC=local',
        ],
    },
    'CN=GG_HR_All,OU=HR,DC=acme,DC=local': {
        'dn': 'CN=GG_HR_All,OU=HR,DC=acme,DC=local',
        'name': 'GG_HR_All', 'type': 'group',
        'description': 'All Human Resources staff',
        'group_type': 'Security Global',
        'when_created': '2018-01-15',
        'members': [
            'CN=Larry Wilson,OU=HR,DC=acme,DC=local',
            'CN=Mary Taylor,OU=HR,DC=acme,DC=local',
        ],
    },
    'CN=GG_Operations_All,OU=Operations,DC=acme,DC=local': {
        'dn': 'CN=GG_Operations_All,OU=Operations,DC=acme,DC=local',
        'name': 'GG_Operations_All', 'type': 'group',
        'description': 'All Operations (warehouse & logistics) staff',
        'group_type': 'Security Global',
        'when_created': '2018-01-15',
        'members': [
            'CN=Nathan Moore,OU=Warehouse,OU=Operations,DC=acme,DC=local',
            'CN=Olivia Jackson,OU=Warehouse,OU=Operations,DC=acme,DC=local',
            'CN=Patrick Harris,OU=Logistics,OU=Operations,DC=acme,DC=local',
            'CN=Quinn Martin,OU=Logistics,OU=Operations,DC=acme,DC=local',
        ],
    },
}

# ─── Group Policy Objects ─────────────────────────────────────────────────────

_GPOS = {
    '{31B2F340-016D-11D2-945F-00C04FB984F9}': {
        'guid': '{31B2F340-016D-11D2-945F-00C04FB984F9}',
        'name': 'Default Domain Policy',
        'status': 'enabled',
        'when_created': '2017-01-01',
        'when_changed': '2023-06-15',
        'description': 'Default domain-wide policy — password, lockout, and Kerberos settings',
        'security_filters': ['Authenticated Users'],
    },
    '{6AC1786C-016F-11D2-945F-00C04FB984F9}': {
        'guid': '{6AC1786C-016F-11D2-945F-00C04FB984F9}',
        'name': 'Default Domain Controllers Policy',
        'status': 'enabled',
        'when_created': '2017-01-01',
        'when_changed': '2022-11-20',
        'description': 'Audit and user-rights assignment policy for domain controllers',
        'security_filters': ['Authenticated Users'],
    },
    '{A1B2C3D4-0000-0000-0000-000000000001}': {
        'guid': '{A1B2C3D4-0000-0000-0000-000000000001}',
        'name': 'Acme Baseline Security',
        'status': 'enabled',
        'when_created': '2019-03-10',
        'when_changed': '2024-09-01',
        'description': 'Corporate security baseline: BitLocker, Windows Firewall, SMB signing',
        'security_filters': ['Authenticated Users'],
    },
    '{B2C3D4E5-0000-0000-0000-000000000002}': {
        'guid': '{B2C3D4E5-0000-0000-0000-000000000002}',
        'name': 'IT Workstation Policy',
        'status': 'enabled',
        'when_created': '2020-01-15',
        'when_changed': '2024-07-22',
        'description': 'IT-specific config: local admin rights, remote management, dev tools',
        'security_filters': ['GG_IT_All'],
    },
    '{C3D4E5F6-0000-0000-0000-000000000003}': {
        'guid': '{C3D4E5F6-0000-0000-0000-000000000003}',
        'name': 'Finance Workstation Policy',
        'status': 'enabled',
        'when_created': '2020-02-01',
        'when_changed': '2024-05-10',
        'description': 'Finance security: restricted USB, encrypted temp files, approved apps only',
        'security_filters': ['Authenticated Users'],
    },
    '{D4E5F607-0000-0000-0000-000000000004}': {
        'guid': '{D4E5F607-0000-0000-0000-000000000004}',
        'name': 'HR Data Protection Policy',
        'status': 'enabled',
        'when_created': '2020-03-05',
        'when_changed': '2023-12-01',
        'description': 'HR data handling: DLP rules, screen timeout, restricted print-to-PDF',
        'security_filters': ['Authenticated Users'],
    },
    '{E5F60718-0000-0000-0000-000000000005}': {
        'guid': '{E5F60718-0000-0000-0000-000000000005}',
        'name': 'Software Deployment - Office Suite',
        'status': 'enabled',
        'when_created': '2021-06-01',
        'when_changed': '2024-10-15',
        'description': 'Microsoft 365 deployment and update channel policy for corporate users',
        'security_filters': ['Authenticated Users'],
    },
    '{F6071829-0000-0000-0000-000000000006}': {
        'guid': '{F6071829-0000-0000-0000-000000000006}',
        'name': 'Screensaver & Lock Policy',
        'status': 'enabled',
        'when_created': '2018-04-01',
        'when_changed': '2023-01-15',
        'description': 'Screen lock after 10 minutes, password-protected screensaver required',
        'security_filters': ['Authenticated Users'],
    },
    '{07182930-0000-0000-0000-000000000007}': {
        'guid': '{07182930-0000-0000-0000-000000000007}',
        'name': 'Service Account Restrictions',
        'status': 'enabled',
        'when_created': '2019-01-15',
        'when_changed': '2024-02-20',
        'description': 'No interactive logon, no RDP, minimal rights for service accounts',
        'security_filters': ['Authenticated Users'],
    },
    '{1829304A-0000-0000-0000-000000000008}': {
        'guid': '{1829304A-0000-0000-0000-000000000008}',
        'name': 'Operations Security Baseline',
        'status': 'enabled',
        'when_created': '2022-01-10',
        'when_changed': '2024-01-05',
        'description': 'Warehouse/logistics workstation hardening — currently link-disabled',
        'security_filters': ['Authenticated Users'],
    },
}

# GPO links: ou_dn → list of link descriptors
# order = processing order (lower = applied last / wins); enforced = can't be blocked
_GPO_LINKS = {
    'DC=acme,DC=local': [
        {'guid': '{31B2F340-016D-11D2-945F-00C04FB984F9}', 'order': 1, 'enforced': True,  'link_enabled': True},
        {'guid': '{A1B2C3D4-0000-0000-0000-000000000001}', 'order': 2, 'enforced': True,  'link_enabled': True},
        {'guid': '{F6071829-0000-0000-0000-000000000006}', 'order': 3, 'enforced': False, 'link_enabled': True},
    ],
    'OU=Corporate,DC=acme,DC=local': [
        {'guid': '{E5F60718-0000-0000-0000-000000000005}', 'order': 1, 'enforced': False, 'link_enabled': True},
    ],
    'OU=IT,DC=acme,DC=local': [
        {'guid': '{B2C3D4E5-0000-0000-0000-000000000002}', 'order': 1, 'enforced': False, 'link_enabled': True},
    ],
    'OU=Finance,DC=acme,DC=local': [
        {'guid': '{C3D4E5F6-0000-0000-0000-000000000003}', 'order': 1, 'enforced': False, 'link_enabled': True},
        {'guid': '{E5F60718-0000-0000-0000-000000000005}', 'order': 2, 'enforced': False, 'link_enabled': True},
    ],
    'OU=HR,DC=acme,DC=local': [
        {'guid': '{D4E5F607-0000-0000-0000-000000000004}', 'order': 1, 'enforced': False, 'link_enabled': True},
        {'guid': '{E5F60718-0000-0000-0000-000000000005}', 'order': 2, 'enforced': False, 'link_enabled': True},
    ],
    'OU=Service_Accounts,DC=acme,DC=local': [
        {'guid': '{07182930-0000-0000-0000-000000000007}', 'order': 1, 'enforced': False, 'link_enabled': True},
    ],
    'OU=Operations,DC=acme,DC=local': [
        {'guid': '{1829304A-0000-0000-0000-000000000008}', 'order': 1, 'enforced': False, 'link_enabled': False},
    ],
}

# OUs that block GPO inheritance from parent containers
_BLOCKS_INHERITANCE = {'OU=Service_Accounts,DC=acme,DC=local'}


# ─── Mock Client ──────────────────────────────────────────────────────────────

class MockADClient:
    """Mimics ADClient interface using static sample data."""

    def get_tree(self):
        domain = dict(_OUS['DC=acme,DC=local'])
        top_level_ous = [
            dict(ou) for ou in _OUS.values()
            if ou.get('type') == 'ou'
            and _get_parent_dn(ou['dn']) == 'DC=acme,DC=local'
        ]
        return {'domain': domain, 'children': top_level_ous}

    def get_ou_contents(self, dn):
        child_ous = [
            dict(ou) for ou in _OUS.values()
            if ou.get('type') == 'ou' and _get_parent_dn(ou['dn']) == dn
        ]
        groups = [
            {'dn': g['dn'], 'name': g['name'], 'type': 'group',
             'description': g.get('description'),
             'member_count': len(g['members'])}
            for g in _GROUPS.values()
            if _get_parent_dn(g['dn']) == dn
        ]
        users = [
            self._user_summary(u) for u in _USERS.values()
            if _get_parent_dn(u['dn']) == dn
        ]
        ou_info = _OUS.get(dn, {})
        return {
            'dn': dn,
            'type': 'ou',
            'name': ou_info.get('name', dn),
            'description': ou_info.get('description'),
            'child_ous': child_ous,
            'groups': groups,
            'users': users,
            'computers': [],
            'counts': {
                'ous': len(child_ous),
                'groups': len(groups),
                'users': len(users),
                'computers': 0,
            },
        }

    def get_group_details(self, dn):
        g = _GROUPS.get(dn)
        if not g:
            return None
        resolved_members = []
        for member_dn in g['members']:
            if member_dn in _USERS:
                resolved_members.append(self._user_summary(_USERS[member_dn]))
            elif member_dn in _GROUPS:
                mg = _GROUPS[member_dn]
                resolved_members.append({
                    'dn': mg['dn'], 'name': mg['name'], 'type': 'group',
                    'member_count': len(mg['members']),
                })
        return {
            'dn': g['dn'], 'name': g['name'], 'type': 'group',
            'description': g.get('description'),
            'group_type': g.get('group_type', 'Security Global'),
            'when_created': g.get('when_created'),
            'members': resolved_members,
            'member_count': len(resolved_members),
            'member_of': [],
        }

    def get_user_details(self, dn):
        u = _USERS.get(dn)
        if not u:
            return None
        enabled = _is_enabled(u['uac'])
        stale = enabled and _is_stale(u['last_logon'])
        alerts = []
        if stale:
            days = (datetime.now() - datetime.fromisoformat(u['last_logon'])).days \
                if u['last_logon'] else None
            msg = (f'Account enabled but no login in {days} days'
                   if days else 'Account enabled but has never logged in')
            alerts.append({'type': 'stale_account', 'severity': 'warning', 'message': msg})

        member_groups = []
        for g_dn in u.get('member_of', []):
            g = _GROUPS.get(g_dn)
            if g:
                member_groups.append({'dn': g['dn'], 'name': g['name'], 'type': 'group'})

        return {
            'dn': u['dn'], 'type': 'user',
            'sam': u['sam'],
            'display_name': u['display_name'],
            'first_name': u['first_name'],
            'last_name': u['last_name'],
            'email': u['email'],
            'phone': u['phone'],
            'department': u['department'],
            'title': u['title'],
            'company': u['company'],
            'enabled': enabled,
            'last_logon': u['last_logon'],
            'when_created': u['when_created'],
            'logon_count': u['logon_count'],
            'bad_pwd_count': u['bad_pwd_count'],
            'member_of': member_groups,
            'stale': stale,
            'alerts': alerts,
            'password_last_set': _days_ago(90),
            'manager': None,
            'direct_reports': [],
        }

    def get_alerts(self):
        alerts = []
        for u in _USERS.values():
            if not _is_enabled(u['uac']):
                continue
            if not _is_stale(u['last_logon']):
                continue
            days = None
            if u['last_logon']:
                days = (datetime.now() - datetime.fromisoformat(u['last_logon'])).days
            ou_dn = _get_parent_dn(u['dn'])
            ou_name = _OUS.get(ou_dn, {}).get('name', ou_dn)
            alerts.append({
                'dn': u['dn'],
                'name': u['display_name'],
                'sam': u['sam'],
                'email': u['email'],
                'department': u['department'],
                'title': u['title'],
                'ou': ou_name,
                'ou_dn': ou_dn,
                'last_logon': u['last_logon'],
                'days_since_login': days,
                'never_logged_in': u['last_logon'] is None,
                'type': 'stale_account',
                'severity': 'warning',
            })
        return sorted(alerts, key=lambda x: x['days_since_login'] or 999999, reverse=True)

    def search(self, query):
        q = query.lower()
        results = []
        for u in _USERS.values():
            if (q in u['display_name'].lower()
                    or q in u['sam'].lower()
                    or (u['email'] and q in u['email'].lower())):
                results.append({
                    'dn': u['dn'], 'name': u['display_name'],
                    'sam': u['sam'], 'type': 'user',
                    'enabled': _is_enabled(u['uac']),
                    'stale': _is_enabled(u['uac']) and _is_stale(u['last_logon']),
                })
        for g in _GROUPS.values():
            if q in g['name'].lower() or (g.get('description') and q in g['description'].lower()):
                results.append({'dn': g['dn'], 'name': g['name'], 'type': 'group'})
        for ou in _OUS.values():
            if ou.get('type') == 'ou' and q in ou['name'].lower():
                results.append({'dn': ou['dn'], 'name': ou['name'], 'type': 'ou'})
        return results[:50]

    def get_stats(self):
        total = len(_USERS)
        enabled = [u for u in _USERS.values() if _is_enabled(u['uac'])]
        stale = [u for u in enabled if _is_stale(u['last_logon'])]
        return {
            'total_users': total,
            'enabled_users': len(enabled),
            'disabled_users': total - len(enabled),
            'stale_accounts': len(stale),
            'total_groups': len(_GROUPS),
            'total_ous': len([o for o in _OUS.values() if o.get('type') == 'ou']),
            'total_computers': 0,
            'domain': _OUS['DC=acme,DC=local']['name'],
            'stale_threshold_days': cfg.STALE_ACCOUNT_DAYS,
        }

    def get_new_today(self):
        """Return users created today with onboarding status fields."""
        today = _today()
        results = []
        for u in _USERS.values():
            wc = u.get('when_created', '')
            if isinstance(wc, str) and wc.startswith(today):
                results.append(self._user_onboarding_summary(u))
        return sorted(results, key=lambda x: x['when_created'], reverse=True)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _user_onboarding_summary(self, u):
        enabled = _is_enabled(u['uac'])
        parent_dn = _get_parent_dn(u['dn'])
        ou_name = _OUS.get(parent_dn, {}).get('name', parent_dn or '')
        groups = [
            {'dn': g_dn, 'name': _GROUPS.get(g_dn, {}).get('name', g_dn)}
            for g_dn in u.get('member_of', [])
        ]
        return {
            'dn': u['dn'],
            'name': u['display_name'],
            'sam': u['sam'],
            'type': 'user',
            'email': u['email'],
            'phone': u['phone'],
            'title': u['title'],
            'department': u['department'],
            'ou_name': ou_name,
            'ou_dn': parent_dn,
            'enabled': enabled,
            'has_logged_in': u['last_logon'] is not None,
            'has_email': bool(u.get('email')),
            'groups': groups,
            'group_count': len(groups),
            'when_created': u['when_created'],
        }

    def get_all_gpos(self):
        """Return all GPOs with computed link counts."""
        link_counts = {}
        for links in _GPO_LINKS.values():
            for link in links:
                link_counts[link['guid']] = link_counts.get(link['guid'], 0) + 1
        result = []
        for g in _GPOS.values():
            result.append({
                'guid': g['guid'],
                'name': g['name'],
                'status': g['status'],
                'when_created': g['when_created'],
                'when_changed': g['when_changed'],
                'description': g['description'],
                'link_count': link_counts.get(g['guid'], 0),
                'security_filters': g['security_filters'],
            })
        return sorted(result, key=lambda x: x['name'])

    def get_gpo_details(self, guid):
        """Return GPO details including all OU links."""
        g = _GPOS.get(guid)
        if not g:
            return None
        linked_ous = []
        for ou_dn, links in _GPO_LINKS.items():
            for link in links:
                if link['guid'] == guid:
                    ou_info = _OUS.get(ou_dn, {})
                    linked_ous.append({
                        'ou_dn': ou_dn,
                        'ou_name': ou_info.get('name', ou_dn),
                        'order': link['order'],
                        'enforced': link['enforced'],
                        'link_enabled': link['link_enabled'],
                    })
        linked_ous.sort(key=lambda x: x['ou_name'])
        return {
            'guid': g['guid'],
            'name': g['name'],
            'status': g['status'],
            'when_created': g['when_created'],
            'when_changed': g['when_changed'],
            'description': g['description'],
            'security_filters': g['security_filters'],
            'linked_ous': linked_ous,
        }

    def get_ou_gpos(self, dn):
        """Return GPOs applied to an OU: direct links + inherited from ancestors."""
        blocks = dn in _BLOCKS_INHERITANCE

        direct_links = []
        for link in _GPO_LINKS.get(dn, []):
            g = _GPOS.get(link['guid'], {})
            direct_links.append({
                'guid': link['guid'],
                'name': g.get('name', link['guid']),
                'order': link['order'],
                'enforced': link['enforced'],
                'link_enabled': link['link_enabled'],
                'source': 'direct',
            })

        inherited_links = []
        parent = _get_parent_dn(dn)
        while parent:
            for link in _GPO_LINKS.get(parent, []):
                if not link['link_enabled']:
                    parent = _get_parent_dn(parent)
                    continue
                # If this OU blocks inheritance, only enforced GPOs pass through
                if blocks and not link['enforced']:
                    continue
                g = _GPOS.get(link['guid'], {})
                parent_info = _OUS.get(parent, {})
                inherited_links.append({
                    'guid': link['guid'],
                    'name': g.get('name', link['guid']),
                    'order': link['order'],
                    'enforced': link['enforced'],
                    'link_enabled': link['link_enabled'],
                    'source': 'inherited',
                    'inherited_from': parent_info.get('name', parent),
                    'inherited_from_dn': parent,
                })
            parent = _get_parent_dn(parent)

        return {
            'dn': dn,
            'blocks_inheritance': blocks,
            'direct': direct_links,
            'inherited': inherited_links,
        }

    def _user_summary(self, u):
        enabled = _is_enabled(u['uac'])
        stale = enabled and _is_stale(u['last_logon'])
        return {
            'dn': u['dn'],
            'name': u['display_name'],
            'sam': u['sam'],
            'type': 'user',
            'email': u['email'],
            'title': u['title'],
            'department': u['department'],
            'enabled': enabled,
            'stale': stale,
            'last_logon': u['last_logon'],
        }
