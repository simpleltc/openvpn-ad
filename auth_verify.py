#!/usr/bin/env python3
from openvpn_ad.config import Config

# These are the configuration parameters for the LDAP server. Replace these with your own values.
ldap_config = Config(
    ldap_host='ldap.yourdomain.com',
    bind_dn='CN=LDAP Bind Account,OU=Users,DC=YourDomain,DC=com',
    bind_secret='a random password',
    base_user_dn='OU=Users,DC=YourDomain,DC=com',
    base_group_dn='OU=Groups,DC=YourDomain,DC=com'
)

# Members of this group will be allowed to connect to the VPN. Replace this with your own value.
authorized_group = 'VPN Users'

# Indicate whether or not logging is enabled
enable_logging = False

### ALL CONFIGURATION DIRECTIVES SHOULD GO ABOVE THIS LINE ###

import sys
import os

from openvpn_ad.utils import configure_logging
from openvpn_ad.verification import verify_creds_against_ad

if __name__ == '__main__':
    logger = configure_logging('auth_verify',enable_logging)
    username = None

    try:
        # The credentials are provided via environment variables from OpenVPN
        username = os.environ['username']
        password = os.environ['password']

        result = verify_creds_against_ad(ldap_config, username, password, authorized_group)

    except:
        result = 1
        logger.exception("An unknown exception occurred.")

    logger.info('Challenge: {0}; Response: {1}'.format(username if username is not None else 'None', result))
    sys.exit(result)


