OpenVPN Active Directory
================================

`openvpn_ad` is a package which provides some helper scripts
that may be of use to sysadmins and developers wishing to use the
open-source [OpenVPN](https://openvpn.net/index.php/open-source/downloads.html)
software while authenticating against Active Directory.

This library includes two helper scripts to use with OpenVPN to facilitate integration
with Active Directory:
* ``on_connect.py`` : This is used with the OpenVPN client-connect option to decide
whether or not a user is permitted to connect based on the certificate signed by
 the approved CA.
* ``auth_verify.py`` : This used with the OpenVPN auth-user-pass-verify option
to decide whether or not the user's credentials are valid.

System Requirements
------------------------
* OpenVPN 2.3
* Python 3
* ldap3 (`pip install python3-ldap`)

Installation
------------------------
1. Install and configure OpenVPN like normal
2. Place the `on_connect.py` file or `auth_verify.py` into your OpenVPN configuration folder (typically /etc/openvpn)
    * Note: `on_connect.py` is for certificate-based authentication, `auth_verify.py` is for username and password-based
3. Replace the `ldap_config` and `authorized_group` variables in the `on_connect.py` or `auth_verify.py` scripts with the configuration for your environment.
3. Install the ``openvpn_ad`` package by running `python3 setup.py`
4. Edit your OpenVPN configuration file and add the appropriate directives (see below)
5. Start / restart OpenVPN

OpenVPN Configuration Directives
-----------------------------------
In order for the scripts to be executed by the OpenVPN server, you must
set some special configuration directives.

### Certificate-based Authentication ###
If you are wanting to use certificates to authenticate, you should add
the following lines to your OpenVPN configuration:

```
script-security 2
client-connect /etc/openvpn/on_connect.py
```

### Username / Password-based Authentication ###
If you are wanting to use usernames and passwords to authenticate, you should
add the following lines to your OpenVPN configuration:

```
script-security 3
auth-user-pass-verify /etc/openvpn/auth_verify.py via-env
```

Troubleshooting
-------------------------------------
If you experience any issues, try turning on logging by editing `on_connect.py`
or `auth_verify.py` and changing `enable_logging = True`. Also further logging
can be enabled from OpenVPN by setting the `log` configuration option. This
option will allow you to see the output of the scripts as well.

On systems with SELinux, it will be very important to make sure that the scripts
have the proper SELinux type set for your environment so that the system
will allow OpenVPN to run them. On Redhat distributions, this is `openvpn_etc_t`.

In addition, some of the dependent Python packages have been known, in certain
circumstances, to be labeled with the wrong SELinux type and as a result the
Python interpreter cannot read the files. These files will have an access denied
error reported in the stack trace that OpenVPN writes to its log. Usually running
`restorecon -r` against the Python site-packages directory will solve the problem.

### Response Codes ###
Both scripts return back a number of response codes. OpenVPN will not permit a
connection if either script returns a non-zero code. These codes are also
written to the log file if logging is enabled and can be useful for
troubleshooting.

Code  | Description                                            |
------|--------------------------------------------------------|
0     | Success                                                |
1     | Unknown Error or Exception                             |
2     | User not found                                         |
3     | User not enabled                                       |
4     | User not a member of the `authorized_group`            |
5     | Invalid Request (Credentials are probably missing)     |
6     | Invalid Credentials (Username & Password do not match) |

License
--------------------------------------------------------
[MIT](https://bitbucket.org/simpleltc/openvpn-ad/raw/master/LICENSE)
