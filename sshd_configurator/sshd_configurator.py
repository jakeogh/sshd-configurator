#!/usr/bin/env python3

import click
import daemon
from .sshd_configurator_daemon import sshd_configurator_daemon

@click.command()
@click.argument('interface', nargs=1)
@click.option('--daemon', is_flag=True)
@click.option('--sshd-config', is_flag=False, default='/etc/ssh/sshd_config')
def sshd_configurator(interface, daemon, sshd_config):
    with daemon.DaemonContext():
        sshd_configurator_daemon(interface=interface, daemon=daemin, sshd_config=sshd_config)


if __name__ == '__main__':
    sshd_configurator()
