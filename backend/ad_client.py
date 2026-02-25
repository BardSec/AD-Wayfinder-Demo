"""
Real Active Directory client using ldap3.
Used when USE_MOCK_DATA=false and a live DC is reachable.
"""
from datetime import datetime, timedelta
from ldap3 import Server, Connection, ALL, NTLM, SUBTREE, BASE, LEVEL
import config as cfg

WINDOWS_EPOCH = datetime(1601, 1, 1)


def _filetime_to_dt(raw):
    """Convert a Windows FILETIME integer (100-ns intervals since 1601) to datetime."""
    try:
        val = int(str(raw))
        if val in (0, 9223372036854775807):
            return None
        return WINDOWS_EPOCH + timedelta(microseconds=val / 10)
    except (TypeError, ValueError, OverflowError):
        return None


def _is_enabled(uac):
    try:
        return not (int(str(uac)) & 0x0002)
    except (TypeError, ValueError):
        return False


def _is_stale(last_logon_dt):
    if last_logon_dt is None:
        return True
    return (datetime.now() - last_logon_dt).days > cfg.STALE_ACCOUNT_DAYS


def _parse_group_type(raw):
    try:
        gt = int(str(raw))
    except (TypeError, ValueError):
        return 'Unknown'
    parts = []
    if gt & 0x00000002:
        parts.append('Global')
    elif gt & 0x00000004:
        parts.append('Domain Local')
    elif gt & 0x00000008:
        parts.append('Universal')
    if gt & 0x80000000:
        parts.append('Security')
    else:
        parts.append('Distribution')
    return ' '.join(parts) if parts else 'Unknown'


def _get_connection():
    server = Server(cfg.AD_HOST, port=cfg.AD_PORT,
                    use_ssl=cfg.AD_USE_SSL, get_info=ALL)
    conn = Connection(
        server,
        user=cfg.AD_USER,
        password=cfg.AD_PASSWORD,
        authentication=NTLM,
        auto_bind=True,
    )
    if cfg.AD_USE_TLS and not cfg.AD_USE_SSL:
        conn.start_tls()
    return conn


class ADClient:
    def __init__(self):
        self._conn = _get_connection()
        self._base = cfg.AD_BASE_DN

    # ── Public API ────────────────────────────────────────────────────────────

    def get_tree(self):
        domain = self._domain_info()
        children = self._list_ous(self._base)
        return {'domain': domain, 'children': children}

    def get_ou_contents(self, dn):
        child_ous = self._list_ous(dn)
        groups = self._list_groups(dn)
        users = self._list_users(dn)
        computers = self._list_computers(dn)
        ou_attrs = self._ou_attrs(dn)
        return {
            'dn': dn, 'type': 'ou',
            'name': ou_attrs.get('name', dn),
            'description': ou_attrs.get('description'),
            'child_ous': child_ous,
            'groups': groups,
            'users': users,
            'computers': computers,
            'counts': {
                'ous': len(child_ous),
                'groups': len(groups),
                'users': len(users),
                'computers': len(computers),
            },
        }

    def get_group_details(self, dn):
        self._conn.search(dn, '(objectClass=group)', search_scope=BASE,
                          attributes=['cn', 'distinguishedName', 'description',
                                      'groupType', 'member', 'memberOf', 'whenCreated'])
        if not self._conn.entries:
            return None
        e = self._conn.entries[0]
        members = []
        for m_dn in (e.member or []):
            info = self._object_summary(str(m_dn))
            if info:
                members.append(info)
        return {
            'dn': str(e.distinguishedName), 'name': str(e.cn), 'type': 'group',
            'description': self._str(e.description),
            'group_type': _parse_group_type(e.groupType),
            'when_created': self._str(e.whenCreated),
            'members': members,
            'member_count': len(members),
            'member_of': [str(g) for g in (e.memberOf or [])],
        }

    def get_user_details(self, dn):
        attrs = [
            'sAMAccountName', 'displayName', 'givenName', 'sn', 'mail',
            'telephoneNumber', 'mobile', 'department', 'title', 'company',
            'manager', 'directReports', 'memberOf', 'userAccountControl',
            'lastLogonTimestamp', 'passwordLastSet', 'whenCreated',
            'description', 'badPwdCount', 'logonCount', 'distinguishedName',
        ]
        self._conn.search(dn, '(objectClass=user)', search_scope=BASE,
                          attributes=attrs)
        if not self._conn.entries:
            return None
        e = self._conn.entries[0]
        uac = e.userAccountControl
        enabled = _is_enabled(uac)
        last_logon = _filetime_to_dt(e.lastLogonTimestamp)
        pw_set = _filetime_to_dt(e.passwordLastSet)
        stale = enabled and _is_stale(last_logon)
        alerts = []
        if stale:
            days = (datetime.now() - last_logon).days if last_logon else None
            msg = (f'Account enabled but no login in {days} days'
                   if days else 'Account enabled but has never logged in')
            alerts.append({'type': 'stale_account', 'severity': 'warning', 'message': msg})
        return {
            'dn': str(e.distinguishedName), 'type': 'user',
            'sam': self._str(e.sAMAccountName),
            'display_name': self._str(e.displayName),
            'first_name': self._str(e.givenName),
            'last_name': self._str(e.sn),
            'email': self._str(e.mail),
            'phone': self._str(e.telephoneNumber),
            'department': self._str(e.department),
            'title': self._str(e.title),
            'company': self._str(e.company),
            'manager': self._str(e.manager),
            'direct_reports': [str(r) for r in (e.directReports or [])],
            'member_of': [str(g) for g in (e.memberOf or [])],
            'enabled': enabled,
            'last_logon': last_logon.isoformat() if last_logon else None,
            'password_last_set': pw_set.isoformat() if pw_set else None,
            'when_created': self._str(e.whenCreated),
            'logon_count': int(str(e.logonCount)) if e.logonCount else 0,
            'bad_pwd_count': int(str(e.badPwdCount)) if e.badPwdCount else 0,
            'stale': stale,
            'alerts': alerts,
        }

    def get_alerts(self):
        self._conn.search(
            self._base,
            '(&(objectClass=user)(objectCategory=person))',
            search_scope=SUBTREE,
            attributes=['sAMAccountName', 'displayName', 'mail', 'department',
                        'title', 'distinguishedName', 'userAccountControl',
                        'lastLogonTimestamp'],
        )
        threshold = datetime.now() - timedelta(days=cfg.STALE_ACCOUNT_DAYS)
        alerts = []
        for e in self._conn.entries:
            if not _is_enabled(e.userAccountControl):
                continue
            last_logon = _filetime_to_dt(e.lastLogonTimestamp)
            if not (last_logon is None or last_logon < threshold):
                continue
            days = (datetime.now() - last_logon).days if last_logon else None
            dn = str(e.distinguishedName)
            ou_dn = dn.split(',', 1)[1] if ',' in dn else dn
            alerts.append({
                'dn': dn,
                'name': self._str(e.displayName) or self._str(e.sAMAccountName),
                'sam': self._str(e.sAMAccountName),
                'email': self._str(e.mail),
                'department': self._str(e.department),
                'title': self._str(e.title),
                'ou': ou_dn,
                'ou_dn': ou_dn,
                'last_logon': last_logon.isoformat() if last_logon else None,
                'days_since_login': days,
                'never_logged_in': last_logon is None,
                'type': 'stale_account',
                'severity': 'warning',
            })
        return sorted(alerts, key=lambda x: x['days_since_login'] or 999999, reverse=True)

    def search(self, query):
        q = query.replace('(', '\\28').replace(')', '\\29').replace('*', '\\2a')
        f = (f'(&(|(objectClass=user)(objectClass=group)(objectClass=organizationalUnit))'
             f'(|(sAMAccountName=*{q}*)(displayName=*{q}*)(cn=*{q}*)(mail=*{q}*)))')
        self._conn.search(self._base, f, search_scope=SUBTREE,
                          attributes=['objectClass', 'cn', 'sAMAccountName',
                                      'displayName', 'distinguishedName',
                                      'userAccountControl', 'ou'])
        results = []
        for e in self._conn.entries:
            classes = [str(c).lower() for c in e.objectClass]
            if 'group' in classes:
                results.append({'dn': str(e.distinguishedName),
                                'name': str(e.cn), 'type': 'group'})
            elif 'organizationalunit' in classes:
                results.append({'dn': str(e.distinguishedName),
                                'name': str(e.ou), 'type': 'ou'})
            elif 'person' in classes:
                results.append({
                    'dn': str(e.distinguishedName), 'type': 'user',
                    'name': self._str(e.displayName) or str(e.sAMAccountName),
                    'sam': str(e.sAMAccountName),
                    'enabled': _is_enabled(e.userAccountControl),
                })
        return results[:50]

    def get_stats(self):
        self._conn.search(
            self._base, '(&(objectClass=user)(objectCategory=person))',
            search_scope=SUBTREE,
            attributes=['userAccountControl', 'lastLogonTimestamp'])
        all_users = self._conn.entries
        enabled = [u for u in all_users if _is_enabled(u.userAccountControl)]
        threshold = datetime.now() - timedelta(days=cfg.STALE_ACCOUNT_DAYS)
        stale = [u for u in enabled
                 if _is_stale(_filetime_to_dt(u.lastLogonTimestamp))]
        self._conn.search(self._base, '(objectClass=group)',
                          search_scope=SUBTREE, attributes=['cn'])
        n_groups = len(self._conn.entries)
        self._conn.search(self._base, '(objectClass=organizationalUnit)',
                          search_scope=SUBTREE, attributes=['ou'])
        n_ous = len(self._conn.entries)
        self._conn.search(self._base, '(objectClass=computer)',
                          search_scope=SUBTREE, attributes=['cn'])
        n_computers = len(self._conn.entries)
        return {
            'total_users': len(all_users),
            'enabled_users': len(enabled),
            'disabled_users': len(all_users) - len(enabled),
            'stale_accounts': len(stale),
            'total_groups': n_groups,
            'total_ous': n_ous,
            'total_computers': n_computers,
            'domain': cfg.AD_BASE_DN,
            'stale_threshold_days': cfg.STALE_ACCOUNT_DAYS,
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _domain_info(self):
        self._conn.search(self._base, '(objectClass=domain)',
                          search_scope=BASE, attributes=['dc', 'distinguishedName'])
        if self._conn.entries:
            e = self._conn.entries[0]
            return {'dn': str(e.distinguishedName),
                    'name': str(e.dc), 'type': 'domain'}
        return {'dn': self._base, 'name': self._base, 'type': 'domain'}

    def _ou_attrs(self, dn):
        self._conn.search(dn, '(objectClass=organizationalUnit)',
                          search_scope=BASE, attributes=['ou', 'description'])
        if self._conn.entries:
            e = self._conn.entries[0]
            return {'name': self._str(e.ou), 'description': self._str(e.description)}
        return {}

    def _list_ous(self, parent_dn):
        self._conn.search(parent_dn, '(objectClass=organizationalUnit)',
                          search_scope=LEVEL,
                          attributes=['ou', 'distinguishedName', 'description'])
        return [{'dn': str(e.distinguishedName), 'name': str(e.ou),
                 'type': 'ou', 'description': self._str(e.description)}
                for e in self._conn.entries]

    def _list_groups(self, parent_dn):
        self._conn.search(parent_dn, '(objectClass=group)',
                          search_scope=LEVEL,
                          attributes=['cn', 'distinguishedName', 'description', 'member'])
        return [{'dn': str(e.distinguishedName), 'name': str(e.cn),
                 'type': 'group', 'description': self._str(e.description),
                 'member_count': len(e.member) if e.member else 0}
                for e in self._conn.entries]

    def _list_users(self, parent_dn):
        self._conn.search(
            parent_dn,
            '(&(objectClass=user)(objectCategory=person))',
            search_scope=LEVEL,
            attributes=['sAMAccountName', 'displayName', 'distinguishedName',
                        'userAccountControl', 'lastLogonTimestamp', 'mail',
                        'title', 'department'],
        )
        results = []
        for e in self._conn.entries:
            enabled = _is_enabled(e.userAccountControl)
            last = _filetime_to_dt(e.lastLogonTimestamp)
            stale = enabled and _is_stale(last)
            results.append({
                'dn': str(e.distinguishedName), 'type': 'user',
                'name': self._str(e.displayName) or str(e.sAMAccountName),
                'sam': str(e.sAMAccountName),
                'email': self._str(e.mail),
                'title': self._str(e.title),
                'department': self._str(e.department),
                'enabled': enabled, 'stale': stale,
                'last_logon': last.isoformat() if last else None,
            })
        return results

    def _list_computers(self, parent_dn):
        self._conn.search(parent_dn, '(objectClass=computer)',
                          search_scope=LEVEL,
                          attributes=['cn', 'distinguishedName',
                                      'operatingSystem', 'lastLogonTimestamp'])
        results = []
        for e in self._conn.entries:
            last = _filetime_to_dt(e.lastLogonTimestamp)
            results.append({
                'dn': str(e.distinguishedName), 'name': str(e.cn),
                'type': 'computer',
                'os': self._str(e.operatingSystem),
                'last_logon': last.isoformat() if last else None,
            })
        return results

    def _object_summary(self, dn):
        self._conn.search(dn, '(objectClass=*)', search_scope=BASE,
                          attributes=['objectClass', 'cn', 'sAMAccountName',
                                      'displayName', 'userAccountControl',
                                      'lastLogonTimestamp', 'mail'])
        if not self._conn.entries:
            return None
        e = self._conn.entries[0]
        classes = [str(c).lower() for c in e.objectClass]
        if 'group' in classes:
            return {'dn': dn, 'name': str(e.cn), 'type': 'group'}
        if 'computer' in classes:
            return {'dn': dn, 'name': str(e.cn), 'type': 'computer'}
        if 'person' in classes or 'user' in classes:
            enabled = _is_enabled(e.userAccountControl)
            last = _filetime_to_dt(e.lastLogonTimestamp)
            return {
                'dn': dn, 'type': 'user',
                'name': self._str(e.displayName) or str(e.cn),
                'sam': self._str(e.sAMAccountName),
                'enabled': enabled,
                'stale': enabled and _is_stale(last),
                'last_logon': last.isoformat() if last else None,
                'email': self._str(e.mail),
            }
        return {'dn': dn, 'name': str(e.cn), 'type': 'object'}

    @staticmethod
    def _str(attr):
        if attr is None:
            return None
        s = str(attr)
        return s if s not in ('[]', 'None', '') else None
