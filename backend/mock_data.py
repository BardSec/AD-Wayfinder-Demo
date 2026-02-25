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

    # ── Internal helpers ──────────────────────────────────────────────────────

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
