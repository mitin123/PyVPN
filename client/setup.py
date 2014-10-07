__author__ = 'amitin'

#!/usr/bin/env python

from distutils.core import setup
import os

packages = {
    'pyvpn.client' : 'PyVPNClient',
}

setup(name='PyVPNClient',
      version='1.0',
      description='Implementation of VPN client for PyVPN server',
      packages = packages,
      package_dir = packages,
      data_files=[
            (
                "/etc/pyvpn",
                [
                    'PyVPNClient/client.conf',
                ]
            ),
      ],
)
