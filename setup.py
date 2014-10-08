from setuptools import setup, find_packages

setup(
    name="openvpn-ad",
    version="0.5",
    description='Code for authenticating OpenVPN against Active Directory',
    author='Mark Adams, Michael Schneider',
    author_email='mark@simpleltc.com, michael@simpleltc.com',
    packages=find_packages(),
    install_requires=['pyasn1==0.1.7', 'python3-ldap==0.9.5.4']
)
