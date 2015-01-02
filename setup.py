__author__ = 'amitin'

#!/usr/bin/env python

from distutils.core import setup
import os

packages = {
    'PyVPN' : 'PyVPN',
}

setup(name='PyVPN',
      version='1.0',
      description='Implementation of VPN client for PyVPN server',
      packages = packages,
      package_dir = {'PyVPN': 'src'},
      data_files=[
            (
                "/etc/pyvpn",
                [
                    'PyVPN/client.conf',
                ]
            ),
      ],
)
