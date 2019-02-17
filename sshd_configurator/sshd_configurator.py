#!/usr/bin/env python3

import click
import daemon
from .sshd_configurator_daemon import sshd_configurator_daemon

@click.command()
@click.argument('interface', nargs=1)
@click.option('--daemon', 'be_daemon', is_flag=True)
@click.option('--sshd-config', is_flag=False, default='/etc/ssh/sshd_config')
def sshd_configurator(interface, be_daemon, sshd_config):
    if be_daemon:
        with daemon.DaemonContext():
            sshd_configurator_daemon(interface=interface, daemon=be_daemon, sshd_config=sshd_config)
    else:
        print("starting with be_daemon:", be_daemon)
        sshd_configurator_daemon(interface=interface, daemon=be_daemon, sshd_config=sshd_config)


if __name__ == '__main__':
    sshd_configurator()
