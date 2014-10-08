import unittest
from unittest.mock import patch, MagicMock
from openvpn_ad.verification import *


class VerifyCertTestCase(unittest.TestCase):
    def test_reformat_dn_from_openvpn(self):
        expected = 'CN=John Smith,OU=Users,DC=MyCompany,DC=com'
        actual = format_dn_from_openvpn('/DC=com/DC=MyCompany/OU=Users/CN=John_Smith')

        self.assertEquals(expected, actual)

    def test_reformat_dn_from_openvpn_should_remove_emailAddress_attribute(self):
        expected = 'CN=John Smith,OU=Users,DC=MyCompany,DC=com'
        actual = format_dn_from_openvpn('/DC=com/DC=MyCompany/OU=Users/CN=John_Smith/emailAddress=john@mycompany.com')

        self.assertEquals(expected, actual)

    @patch('openvpn_ad.verification.ActiveDirectoryProvider')
    def test_verify_cert_should_return_not_found_if_user_invalid(self, ad_provider):
        ad_provider().get_username_from_dn.return_value = None

        config = MagicMock()
        expected = ReturnCode.user_not_found
        actual = verify_cert_against_ad(config,
                                        '/DC=com/DC=MyCompany/OU=Users/CN=John_Smith/emailAddress=john@mycompany.com',
                                        'VPN Group')

        self.assertEquals(expected, actual)

    @patch('openvpn_ad.verification.ActiveDirectoryProvider')
    def test_verify_cert_should_return_not_enabled_if_user_disabled(self, ad_provider):
        ad_provider().get_username_from_dn.return_value = 'john.doe'
        ad_provider().is_enabled.return_value = False

        config = MagicMock()
        expected = ReturnCode.user_not_enabled
        actual = verify_cert_against_ad(config,
                                        '/DC=com/DC=MyCompany/OU=Users/CN=John_Smith/emailAddress=john@mycompany.com',
                                        'VPN Group')

        self.assertEquals(expected, actual)

    @patch('openvpn_ad.verification.ActiveDirectoryProvider')
    def test_verify_cert_should_return_not_in_group_if_user_not_group_member(self, ad_provider):
        ad_provider().get_username_from_dn.return_value = 'john.doe'
        ad_provider().is_enabled.return_value = True
        ad_provider().is_group_member.return_value = False

        config = MagicMock()
        expected = ReturnCode.user_not_group_member
        actual = verify_cert_against_ad(config,
                                        '/DC=com/DC=MyCompany/OU=Users/CN=John_Smith/emailAddress=john@mycompany.com',
                                        'VPN Group')

        self.assertEquals(expected, actual)

    @patch('openvpn_ad.verification.ActiveDirectoryProvider')
    def test_verify_cert_should_return_success_if_user_valid_enabled_and_in_group(self, ad_provider):
        ad_provider().get_username_from_dn.return_value = 'john.doe'
        ad_provider().is_enabled.return_value = True
        ad_provider().is_group_member.return_value = True

        config = MagicMock()
        expected = ReturnCode.success
        actual = verify_cert_against_ad(config,
                                        '/DC=com/DC=MyCompany/OU=Users/CN=John_Smith/emailAddress=john@mycompany.com',
                                        'VPN Group')

        self.assertEquals(expected, actual)

class VerifyUserPassTestCase(unittest.TestCase):

    @patch('openvpn_ad.verification.ActiveDirectoryProvider')
    def test_verify_cert_should_return_user_not_found_if_no_account_matches(self, ad_provider):
        ad_provider().get_dn_from_username.side_effect = [None]

        config = MagicMock()
        expected = ReturnCode.user_not_found
        actual = verify_creds_against_ad(config, 'john.smith', 'johnspassword1', 'VPN Group')

        self.assertEquals(expected, actual)

    @patch('openvpn_ad.verification.ActiveDirectoryProvider')
    def test_verify_cert_should_return_invalid_creds_if_authentication_fails(self, ad_provider):
        ad_provider().get_dn_from_username.return_value = 'fake_dn'
        ad_provider().authenticate.return_value = False

        config = MagicMock()
        expected = ReturnCode.invalid_creds
        actual = verify_creds_against_ad(config, 'john.smith', 'johnspassword1', 'VPN Group')

        self.assertEquals(expected, actual)

    @patch('openvpn_ad.verification.ActiveDirectoryProvider')
    def test_verify_cert_should_return_not_enabled_if_user_disabled(self, ad_provider):
        ad_provider().get_dn_from_username.return_value = 'fake_dn'
        ad_provider().authenticate.return_value = True
        ad_provider().is_enabled.return_value = False

        config = MagicMock()
        expected = ReturnCode.user_not_enabled
        actual = verify_creds_against_ad(config, 'john.smith', 'johnspassword1', 'VPN Group')

        self.assertEquals(expected, actual)

    @patch('openvpn_ad.verification.ActiveDirectoryProvider')
    def test_verify_cert_should_return_not_in_group_if_user_not_group_member(self, ad_provider):
        ad_provider().get_dn_from_username.return_value = 'fake_dn'
        ad_provider().authenticate.return_value = True
        ad_provider().is_enabled.return_value = True
        ad_provider().is_group_member.return_value = False

        config = MagicMock()
        expected = ReturnCode.user_not_group_member
        actual = verify_creds_against_ad(config, 'john.smith', 'johnspassword1', 'VPN Group')

        self.assertEquals(expected, actual)

    @patch('openvpn_ad.verification.ActiveDirectoryProvider')
    def test_verify_cert_should_return_success_if_user_valid_enabled_and_in_group(self, ad_provider):
        ad_provider().get_dn_from_username.return_value = 'fake_dn'
        ad_provider().authenticate.return_value = True
        ad_provider().is_enabled.return_value = True
        ad_provider().is_group_member.return_value = True

        config = MagicMock()
        expected = ReturnCode.success
        actual = verify_creds_against_ad(config, 'john.smith', 'johnspassword1', 'VPN Group')

        self.assertEquals(expected, actual)

