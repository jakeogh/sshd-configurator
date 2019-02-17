#!/usr/bin/env python3

import click
import logging
import attr
from daemonize import Daemonize
from .sshd_configurator_daemon import sshd_configurator_daemon

global pidfile
pidfile = "/run/sshd-configurator.pid"

global logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
fh = logging.StreamHandler()
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
global keep_fds
keep_fds = [fh.stream.fileno()]


@attr.s(auto_attribs=True)
class SSHD_CONFIGURATOR():
    interface: str
    daemon: bool
    sshd_config: str
    logger: logging

    def run(self):
        print("run")
        sshd_configurator_daemon(interface=self.interface, daemon=self.daemon, sshd_config=self.sshd_config, logger=self.logger)


@click.command()
@click.argument('interface', nargs=1)
@click.option('--daemon', is_flag=True)
@click.option('--sshd-config', is_flag=False, default='/etc/ssh/sshd_config')
def sshd_configurator(interface, daemon, sshd_config):
    global keep_fds
    global pidfile
    global logger
    foreground = not daemon
    print("foreground:", foreground)
    sshd_configurator_obj = SSHD_CONFIGURATOR(interface=interface, daemon=daemon, sshd_config=sshd_config, logger=logger)
    daemon = Daemonize(app="ssh_configurator", pid=pidfile, action=sshd_configurator_obj.run, foreground=foreground, keep_fds=keep_fds)
    daemon.start()


if __name__ == '__main__':
    sshd_configurator()
