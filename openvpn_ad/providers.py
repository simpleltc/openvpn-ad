import ldap3 as ldap


class ActiveDirectoryProvider(object):
    def __init__(self, server, bind_dn, bind_secret, base_user_dn, base_group_dn):
        self.server = ldap.Server(server, use_ssl=True)
        self.bind_dn = bind_dn
        self.bind_secret = bind_secret
        self.base_user_dn = base_user_dn
        self.base_group_dn = base_group_dn

    def _get_ldap_connection(self, user_dn=None, password=None):

        if user_dn is None:
            user_dn = self.bind_dn
            password = self.bind_secret

        con = ldap.Connection(self.server, user=user_dn, password=password)
        con.open()

        if not con.bind():
            raise ConnectionError("Couldn't bind to LDAP server.")

        return con

    def get_username_from_dn(self, user_dn):
        """Retrieves the username (sAMAccountName) associated with the specified distinguished name (DN)"""
        filt = '(&(objectClass=user)(distinguishedName=' + user_dn + '))'
        attr = ['sAMAccountName']

        with self._get_ldap_connection() as con:
            con.search(self.base_user_dn, filt, ldap.SEARCH_SCOPE_WHOLE_SUBTREE, attributes=attr)
            result = con.response

        if result is None or len(result) == 0:
            return None

        return result[0]['attributes']['sAMAccountName'][0]


    def get_dn_from_username(self, username):
        """Retrieves the username (sAMAccountName) associated with the specified distinguished name (DN)"""
        filt = '(&(objectClass=user)(sAMAccountName=' + username + '))'
        attr = ['sAMAccountName']

        with self._get_ldap_connection() as con:
            con.search(self.base_user_dn, filt, ldap.SEARCH_SCOPE_WHOLE_SUBTREE, attributes=attr)
            result = con.response

        if result is None or len(result) == 0:
            return None

        return result[0]['dn']


    def authenticate(self, username, password):
        """Authenticates against Active Directory based on the provided username and password"""
        filt = '(&(objectClass=user)(sAMAccountName=' + username + ')(!(userAccountControl:1.2.840.113556.1.4.803:=2)))'
        attr = ['sAMAccountName']

        with self._get_ldap_connection() as con:
            con.search(self.base_user_dn, filt, ldap.SEARCH_SCOPE_WHOLE_SUBTREE, attributes=attr)
            result = con.response

            if result is None or len(result) == 0:
                return False

            user_dn = result[0]['dn']

        try:
            self._get_ldap_connection(user_dn, password)
            return True
        except:
            return False

        return False


    def is_enabled(self, username):
        filter_query = '(&(objectClass=user)(sAMAccountName=' + username + ')(!(userAccountControl:1.2.840.113556.1.4.803:=2)))'
        attr = ['sAMAccountName']

        with self._get_ldap_connection() as con:
            con.search(self.base_user_dn, filter_query, ldap.SEARCH_SCOPE_WHOLE_SUBTREE, attributes=attr)
            result = con.response

        if result is not None and len(result) > 0:
            return True

        return False

    def get_user_groups(self, username):
        user_dn = self.get_dn_from_username(username)

        filter_query = '(&(objectClass=group)(member:1.2.840.113556.1.4.1941:=' + user_dn + '))'
        attr = ['sAMAccountName']

        with self._get_ldap_connection() as con:
            con.search(self.base_group_dn, filter_query, ldap.SEARCH_SCOPE_WHOLE_SUBTREE, attributes=attr)

            result = con.response

            if result is None or len(result) == 0:
                return []

        return [entry['attributes']['sAMAccountName'][0] for entry in result]

    def is_group_member(self, username, group):
        return group in self.get_user_groups(username)