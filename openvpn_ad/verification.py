from collections import OrderedDict

from openvpn_ad.providers import ActiveDirectoryProvider


class ReturnCode(object):
    success = 0
    unknown_err = 1
    user_not_found = 2
    user_not_enabled = 3
    user_not_group_member = 4
    invalid_request = 5
    invalid_creds = 6

def format_dn_from_openvpn(cert):
    parts = [part.split('=') for part in reversed(cert.replace('_', ' ').split('/')) if '=' in part]
    parts = filter(lambda x: x[0] != 'emailAddress', parts)

    return ','.join(map('='.join, parts))

def verify_cert_against_ad(config, cert, group):
    """ Given a verified certificate DN from OpenVPN and a group DN from Active Directory, determines if
    the specified user's account exists, is enabled, and is a member of the specified group
    :param config: Config object containing the LDAP configuration
    :param cert: The certificate TLS ID provided by OpenVPN
    :param group: The DN of the Active Directory group that the user must be a member of
    :return: a ReturnCode value indicating whether or not the certificate is valid for a VPN connection
    """

    ad_auth = ActiveDirectoryProvider(config.ldap_host, config.bind_dn, config.bind_secret, config.base_user_dn,
                                      config.base_group_dn)

    user_dn = format_dn_from_openvpn(cert)
    username = ad_auth.get_username_from_dn(user_dn)

    if username is None:
        return ReturnCode.user_not_found

    is_enabled = ad_auth.is_enabled(username)

    if not is_enabled:
        return ReturnCode.user_not_enabled

    is_group_member = ad_auth.is_group_member(username, group)

    if not is_group_member:
        return ReturnCode.user_not_group_member

    return ReturnCode.success


def verify_creds_against_ad(config, username, password, group):
    """ Given the credentials from the user and the group DN for an Active Directory Group, determine whether or not
    the credentials are valid and the user account exists, is enabled, and is part of the specified group.
    :param config
    :param username:
    :param password:
    :param group: The DN of the Active Directory group that the user must be a member of
    :return: a ReturnCode value indicating whether or not the credentials are valid
    """
    ad_auth = ActiveDirectoryProvider(config.ldap_host, config.bind_dn, config.bind_secret, config.base_user_dn,
                                      config.base_group_dn)

    if username is None or password is None:
        return ReturnCode.invalid_request

    user_dn = ad_auth.get_dn_from_username(username)

    if user_dn is None:
        return ReturnCode.user_not_found

    is_authenticated = ad_auth.authenticate(username, password)

    if not is_authenticated:
        return ReturnCode.invalid_creds

    is_enabled = ad_auth.is_enabled(username)

    if not is_enabled:
        return ReturnCode.user_not_enabled

    is_group_member = ad_auth.is_group_member(username, group)

    if not is_group_member:
        return ReturnCode.user_not_group_member

    return ReturnCode.success
