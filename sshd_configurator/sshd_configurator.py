#!/usr/bin/env python3

import click
import attr
from daemonize import Daemonize
from .sshd_configurator_daemon import sshd_configurator_daemon

global pidfile
pidfile = "/run/sshd-configurator.pid"

@attr.s(auto_attribs=True)
class SSHD_CONFIGURATOR():
    interface: str
    daemon: bool
    sshd_config: str

    def run(self):
        print("run")
        sshd_configurator_daemon(interface=self.interface, daemon=self.daemon, sshd_config=self.sshd_config)


@click.command()
@click.argument('interface', nargs=1)
@click.option('--daemon', is_flag=True)
@click.option('--sshd-config', is_flag=False, default='/etc/ssh/sshd_config')
def sshd_configurator(interface, daemon, sshd_config):
    foreground = not daemon
    print("foreground:", foreground)
    sshd_configurator_obj = SSHD_CONFIGURATOR(interface=interface, daemon=daemon, sshd_config=sshd_config)
    daemon = Daemonize(app="ssh_configurator", pid=pidfile, action=sshd_configurator_obj.run, foreground=foreground)
    daemon.start()


if __name__ == '__main__':
    sshd_configurator()
