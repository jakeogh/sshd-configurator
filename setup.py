# -*- coding: utf-8 -*-
"""
sshd-configurator
"""
import sys
if not sys.version_info[0] == 3:
    sys.exit("Sorry, Python 3 is required. Use: \'python3 setup.py install\'")

from setuptools import find_packages, setup
dependencies = []
version = 0.01

setup(
    name="sshd-configurator",
    version=version,
    url="https://github.com/jakeogh/sshd-configurator",
    license='MIT',
    author="jakeogh",
    author_email="github.com@v6y.net",
    description='Manage sshd config',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'sshd-configurator = sshd_configurator.sshd_configurator:sshd_configurator',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
