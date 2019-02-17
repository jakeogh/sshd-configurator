#!/usr/bin/env python3

import daemon
from .sshd_configurator_daemon import sshd_configurator_daemon

if __name__ == '__main__':
    with daemon.DaemonContext():
        sshd_configurator_daemon()
