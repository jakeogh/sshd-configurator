#!/usr/bin/env python3

import daemon
from .sshd_configurator_daemon import sshd_configurator_daemon


def sshd_configurator():
    with daemon.DaemonContext():
        sshd_configurator_daemon()


if __name__ == '__main__':
    sshd_configurator()
