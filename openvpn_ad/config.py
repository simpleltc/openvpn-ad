class Config(object):
    def __init__(self, ldap_host, bind_dn, bind_secret, base_user_dn, base_group_dn):
        self.ldap_host = ldap_host
        self.bind_dn = bind_dn
        self.bind_secret = bind_secret
        self.base_user_dn = base_user_dn
        self.base_group_dn = base_group_dn
